"""
Vector store for storing and retrieving document chunks.

This module handles persistence and retrieval of embedded document chunks using ChromaDB.
Defaults to local persistent storage for testing and demo purposes.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ..ingestion.chunker import ChunkMetadata


class VectorStore:
    """
    Vector store for document chunks using ChromaDB.
    
    Defaults to local persistent storage for testing and demo purposes.
    Data is stored in the specified directory (or in-memory if no directory provided).
    """
    
    COLLECTION_NAME = "document_chunks"
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Directory to persist the vector store.
                              If None, uses in-memory storage (data lost on restart).
                              For testing/demo, use a local directory like Path("data/chroma_db")
        """
        self.persist_directory = Path(persist_directory) if persist_directory else None
        self._collection = None
        self._client = None
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                
                if self.persist_directory:
                    self._client = chromadb.PersistentClient(
                        path=str(self.persist_directory),
                        settings=Settings(anonymized_telemetry=False)
                    )
                else:
                    self._client = chromadb.Client(
                        settings=Settings(anonymized_telemetry=False)
                    )
                
                self._collection = self._client.get_or_create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
            except ImportError:
                raise ImportError(
                    "chromadb is required. Install with: uv pip install chromadb"
                )
    
    @staticmethod
    def _convert_metadata(chunk_meta: ChunkMetadata) -> Dict[str, Any]:
        """Convert ChunkMetadata to dict compatible with ChromaDB."""
        metadata_dict = chunk_meta.model_dump()
        
        # Convert to ChromaDB-compatible types
        result = {}
        for key, value in metadata_dict.items():
            if value is None:
                continue  # Skip None values
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif hasattr(value, 'value'):  # Enum
                result[key] = str(value.value)
            elif isinstance(value, (str, int, float, bool)):
                result[key] = value
            else:
                result[key] = str(value)
        
        return result
    
    def add_chunks(
        self,
        chunks: List[Tuple[str, ChunkMetadata]],
        embeddings: List[List[float]],
        batch_size: int = 100
    ):
        """
        Add chunks with embeddings to the vector store.
        
        Args:
            chunks: List of (chunk_text, chunk_metadata) tuples
            embeddings: List of embedding vectors
            batch_size: Batch size for adding chunks
        """
        self._initialize_chroma()
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            
            ids, texts, metadatas, embeds = [], [], [], []
            
            for (chunk_text, chunk_meta), embedding in zip(batch_chunks, batch_embeddings):
                ids.append(chunk_meta.chunk_id)
                texts.append(chunk_text)
                metadatas.append(self._convert_metadata(chunk_meta))
                embeds.append(embedding)
            
            self._collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeds,
                metadatas=metadatas
            )
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_dict: Optional metadata filters (e.g., {"document_category": "company"})
        
        Returns:
            List of search results with chunk text and metadata
        """
        self._initialize_chroma()
        
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict
        )
        
        if not results['ids'] or not results['ids'][0]:
            return []
        
        distances = results.get('distances', [[]])[0] if 'distances' in results else [None] * len(results['ids'][0])
        
        return [
            {
                'chunk_id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': distances[i] if i < len(distances) else None
            }
            for i in range(len(results['ids'][0]))
        ]
    
    def delete_collection(self):
        """Delete the entire collection (use with caution)."""
        self._initialize_chroma()
        if self._collection:
            self._client.delete_collection(name=self.COLLECTION_NAME)
            self._collection = None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        self._initialize_chroma()
        return {
            'total_chunks': self._collection.count(),
            'collection_name': self.COLLECTION_NAME
        }
