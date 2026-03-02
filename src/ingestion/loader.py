"""
Document loading utilities.

This module handles loading documents from the knowledge base.
"""

from pathlib import Path
from typing import List, Tuple, Optional
from .metadata import DocumentMetadata, extract_document_metadata


def get_knowledge_base_path() -> Path:
    """
    Get the default knowledge base directory path.
    
    Returns:
        Path to the knowledge-base directory
    """
    # Get the project root (assuming src/ingestion/loader.py structure)
    # Go up from src/ingestion/loader.py -> src/ingestion -> src -> project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    return project_root / "knowledge-base"


def load_documents(path: Optional[Path] = None) -> List[Tuple[str, DocumentMetadata]]:
    """
    Load document(s) from a file or directory.
    
    If path is a file, returns a list with one document.
    If path is a directory, returns all markdown documents in the directory.
    If path is None, defaults to the knowledge-base directory.
    
    Args:
        path: Path to a document file or directory containing documents.
              If None, defaults to the knowledge-base directory.
    
    Returns:
        List of tuples: (content, metadata) for each document
    """
    if path is None:
        path = get_knowledge_base_path()
    
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    
    documents = []
    
    if path.is_file():
        # Single file
        if path.suffix.lower() != '.md':
            raise ValueError(f"Only markdown files (.md) are supported, got: {path.suffix}")
        
        try:
            content = path.read_text(encoding='utf-8')
            metadata = extract_document_metadata(path, content)
            documents.append((content, metadata))
        except Exception as e:
            raise RuntimeError(f"Failed to load {path}: {e}") from e
    
    elif path.is_dir():
        # Directory - find all markdown files
        for file_path in path.rglob("*.md"):
            # Skip README files
            if file_path.name.lower() == "readme.md":
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                metadata = extract_document_metadata(file_path, content)
                documents.append((content, metadata))
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")
                continue
    else:
        raise ValueError(f"Path must be a file or directory: {path}")
    
    return documents
