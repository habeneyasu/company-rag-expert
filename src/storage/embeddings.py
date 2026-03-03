"""
Embedding generation for document chunks.

This module handles generating vector embeddings for text chunks.
"""

import os
import warnings
from typing import List

# Suppress HuggingFace warnings globally
os.environ.setdefault("HF_HUB_DISABLE_EXPERIMENTAL_WARNING", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*HF Hub.*")


class EmbeddingModel:
    """Wrapper for embedding model."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model.
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        self._model = None
    
    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required. Install with: uv pip install sentence-transformers"
                )
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats representing the embedding vector
        """
        self._load_model()
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
        
        Returns:
            List of embedding vectors
        """
        self._load_model()
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100
        )
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension
        """
        self._load_model()
        # Test with a dummy text to get dimension
        test_embedding = self._model.encode("test", convert_to_numpy=True)
        return len(test_embedding)
