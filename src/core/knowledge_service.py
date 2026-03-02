"""
Knowledge service orchestrator.

This module orchestrates the complete RAG pipeline:
1. Load documents (loader → metadata)
2. Chunk documents (chunker)
3. Generate embeddings (embeddings)
4. Store in vector database (vector_store)
"""

from pathlib import Path
from typing import Optional, Dict, Any
from tqdm import tqdm

from ..ingestion.loader import get_knowledge_base_path, load_documents
from ..ingestion.chunker import chunk_document
from ..storage.embeddings import EmbeddingModel
from ..storage.vector_store import VectorStore


class KnowledgeService:
    """Orchestrates document ingestion: loading, chunking, embedding, and storage."""
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_model: Optional[EmbeddingModel] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize knowledge service.
        
        Args:
            vector_store: Vector store instance (creates default if None)
            embedding_model: Embedding model instance (creates default if None)
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.vector_store = vector_store or VectorStore()
        self.embedding_model = embedding_model or EmbeddingModel()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def _process_document(self, content: str, metadata) -> int:
        """
        Process a document: chunk, embed, and store.
        
        Args:
            content: Document content
            metadata: Document metadata
        
        Returns:
            Number of chunks processed
        """
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
        """
        Ingest documents from a file or directory.
        
        Args:
            path: File or directory path (defaults to knowledge-base if None)
            show_progress: Show progress bar
        
        Returns:
            Dictionary with ingestion statistics
        """
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


def ingest_knowledge_base(
    knowledge_base_path: Optional[Path] = None,
    vector_store_path: Optional[Path] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to ingest the knowledge base.
    
    Uses local ChromaDB storage for testing and demo purposes.
    Data is persisted to the specified directory (or in-memory if not specified).
    
    Args:
        knowledge_base_path: Path to knowledge base directory (defaults to knowledge-base if None)
        vector_store_path: Optional directory for ChromaDB persistence (defaults to in-memory if None)
                          For testing/demo, use: Path("data/chroma_db")
        chunk_size: Size of chunks in characters
        chunk_overlap: Overlap between chunks in characters
        show_progress: Whether to show progress bar
    
    Returns:
        Dictionary with ingestion statistics
    """
    service = KnowledgeService(
        vector_store=VectorStore(persist_directory=vector_store_path),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return service.ingest(knowledge_base_path, show_progress)
