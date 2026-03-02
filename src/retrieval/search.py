"""
Semantic search for document chunks.

This module handles searching the vector store for relevant chunks.
"""

from typing import List, Dict, Any, Optional
from ..storage.vector_store import VectorStore
from ..storage.embeddings import EmbeddingModel


class SearchEngine:
    """Semantic search engine for document chunks."""
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_model: Optional[EmbeddingModel] = None
    ):
        """
        Initialize search engine.
        
        Args:
            vector_store: Vector store instance (creates default if None)
            embedding_model: Embedding model instance (creates default if None)
        """
        self.vector_store = vector_store or VectorStore()
        self.embedding_model = embedding_model or EmbeddingModel()
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_dict: Optional metadata filters (e.g., {"document_category": "company"})
        
        Returns:
            List of search results with chunk text and metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_dict=filter_dict
        )
        
        return results
