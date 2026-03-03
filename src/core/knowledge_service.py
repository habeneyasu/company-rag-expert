"""Knowledge service orchestrator for RAG pipeline."""

from pathlib import Path
from typing import Optional, Dict, Any
from tqdm import tqdm

from ..ingestion.loader import get_knowledge_base_path, load_documents
from ..ingestion.chunker import chunk_document
from ..storage.embeddings import EmbeddingModel
from ..storage.vector_store import VectorStore
from ..retrieval.search import SearchEngine
from ..retrieval.reranker import Reranker
from ..generation.prompt import PromptBuilder
from ..generation.llm_client import LLMClient


class KnowledgeService:
    """Orchestrates complete RAG pipeline: ingestion and querying."""
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_model: Optional[EmbeddingModel] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_reranker: bool = True,
        max_context_chunks: Optional[int] = None
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_model = embedding_model or EmbeddingModel()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_reranker = use_reranker
        self.max_context_chunks = max_context_chunks
        
        # Initialize retrieval and generation components
        self.search_engine = SearchEngine(
            vector_store=self.vector_store,
            embedding_model=self.embedding_model
        )
        self.reranker = Reranker() if use_reranker else None
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()
    
    def _process_document(self, content: str, metadata) -> int:
        """Process a document: chunk, embed, and store."""
        # Chunk document
        chunks = chunk_document(content, metadata, self.chunk_size, self.chunk_overlap)
        if not chunks:
            return 0
        
        # Generate embeddings
        chunk_texts = [text for text, _ in chunks]
        embeddings = self.embedding_model.embed_batch(chunk_texts)
        
        # Store in vector database
        self.vector_store.add_chunks(chunks, embeddings)
        return len(chunks)
    
    def ingest(self, path: Optional[Path] = None, show_progress: bool = True) -> Dict[str, Any]:
        """Ingest documents from a file or directory."""
        if path is None:
            path = get_knowledge_base_path()
        
        # Load documents (loader handles metadata extraction internally)
        documents = load_documents(path)
        if not documents:
            return {'documents_processed': 0, 'total_chunks': 0, 'errors': []}
        
        total_chunks = 0
        errors = []
        iterator = tqdm(documents, desc="Ingesting") if show_progress else documents
        
        for content, metadata in iterator:
            try:
                total_chunks += self._process_document(content, metadata)
            except Exception as e:
                error_msg = f"Error processing {metadata.source_path}: {str(e)}"
                errors.append(error_msg)
                if show_progress:
                    tqdm.write(error_msg)
        
        return {
            'documents_processed': len(documents) - len(errors),
            'total_chunks': total_chunks,
            'errors': errors
        }
    
    def query(
        self,
        query: str,
        n_results: int = 10,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        generate_answer: bool = True
    ) -> Dict[str, Any]:
        """Query the knowledge base and generate answer."""
        # Search
        results = self.search_engine.search(query, n_results=n_results, filter_dict=filter_dict)
        
        # Rerank if enabled
        reranked = self.reranker.rerank(query, results, top_k=top_k) if self.reranker else results[:top_k]
        
        response = {
            'query': query,
            'search_results': results,
            'reranked_results': reranked
        }
        
        # Generate answer if requested
        if generate_answer:
            prompt = self.prompt_builder.build_prompt(
                query=query,
                results=reranked,
                max_context_chunks=self.max_context_chunks
            )
            answer = self.llm_client.generate(
                system_prompt=prompt['system'],
                user_prompt=prompt['user']
            )
            response['answer'] = answer
        
        return response


def ingest_knowledge_base(
    knowledge_base_path: Optional[Path] = None,
    vector_store_path: Optional[Path] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    show_progress: bool = True
) -> Dict[str, Any]:
    """Convenience function to ingest the knowledge base."""
    service = KnowledgeService(
        vector_store=VectorStore(persist_directory=vector_store_path),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return service.ingest(knowledge_base_path, show_progress)
