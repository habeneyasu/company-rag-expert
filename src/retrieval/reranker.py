"""
Reranking search results for improved relevance.

This module reranks initial search results using cross-encoder models.
"""

from typing import List, Dict, Any, Optional


class Reranker:
    """Reranker for improving search result relevance."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranker.
        
        Args:
            model_name: Cross-encoder model name for reranking
        """
        self.model_name = model_name
        self._model = None
    
    def _load_model(self):
        """Lazy load the reranking model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required. Install with: pip install sentence-transformers"
                )
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank search results for better relevance.
        
        Args:
            query: Original search query
            results: Initial search results from vector store
            top_k: Number of top results to return (None = return all)
        
        Returns:
            Reranked list of results with relevance scores
        """
        if not results:
            return []
        
        self._load_model()
        
        # Prepare query-document pairs
        pairs = [[query, result['text']] for result in results]
        
        # Get relevance scores
        scores = self._model.predict(pairs)
        
        # Add scores and sort by relevance
        for i, result in enumerate(results):
            result['relevance_score'] = float(scores[i])
        
        # Sort by relevance (higher is better)
        reranked = sorted(results, key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top_k if specified
        return reranked[:top_k] if top_k else reranked
