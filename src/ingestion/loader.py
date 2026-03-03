"""Document loading utilities."""

from pathlib import Path
from typing import List, Tuple, Optional
from .metadata import DocumentMetadata, extract_document_metadata


def get_knowledge_base_path() -> Path:
    """Get the default knowledge base directory path."""
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    return project_root / "knowledge-base"


def load_documents(path: Optional[Path] = None) -> List[Tuple[str, DocumentMetadata]]:
    """Load document(s) from a file or directory."""
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
            except Exception:
                continue
    else:
        raise ValueError(f"Path must be a file or directory: {path}")
    
    return documents
