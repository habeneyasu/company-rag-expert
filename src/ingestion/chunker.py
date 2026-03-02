"""
Document chunking and chunk metadata.

This module handles splitting documents into chunks and creating metadata for each chunk.
"""

from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field
from .metadata import DocumentMetadata, DocumentCategory


class ChunkMetadata(BaseModel):
    """Simple metadata schema for a document chunk."""
    
    # Chunk identification
    chunk_id: str = Field(..., description="Unique chunk identifier")
    chunk_index: int = Field(..., description="Chunk position in document (0-based)")
    total_chunks: int = Field(..., description="Total number of chunks")
    
    # Reference to parent document
    document_source_path: str = Field(..., description="Source document path")
    document_category: DocumentCategory = Field(..., description="Document category")
    
    # Chunk info
    section: Optional[str] = Field(None, description="Section name")
    chunk_size: int = Field(..., description="Chunk size in characters")
    
    class Config:
        use_enum_values = True


def chunk_document(
    content: str,
    document_metadata: DocumentMetadata,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Tuple[str, ChunkMetadata]]:
    """
    Split document content into chunks and create metadata for each chunk.
    
    Args:
        content: Document content to chunk
        document_metadata: Metadata of the parent document
        chunk_size: Target size of each chunk in characters
        chunk_overlap: Overlap between chunks in characters
    
    Returns:
        List of tuples: (chunk_text, chunk_metadata)
    """
    chunks = []
    content_length = len(content)
    
    # Simple chunking: split by size with overlap
    start = 0
    chunk_index = 0
    
    while start < content_length:
        end = min(start + chunk_size, content_length)
        chunk_text = content[start:end]
        
        # Try to find section/heading for this chunk
        section = _extract_section(chunk_text, content, start)
        
        # Create chunk metadata
        chunk_id = f"{document_metadata.filename}_chunk_{chunk_index}"
        chunk_meta = ChunkMetadata(
            chunk_id=chunk_id,
            chunk_index=chunk_index,
            total_chunks=0,  # Will update after all chunks are created
            document_source_path=document_metadata.source_path,
            document_category=document_metadata.category,
            chunk_size=len(chunk_text),
            section=section
        )
        
        chunks.append((chunk_text, chunk_meta))
        
        # Move to next chunk with overlap
        start = end - chunk_overlap if end < content_length else end
        chunk_index += 1
    
    # Update total_chunks in all metadata
    for _, chunk_meta in chunks:
        chunk_meta.total_chunks = len(chunks)
    
    return chunks


def create_chunk_metadata(
    chunk_id: str,
    chunk_index: int,
    total_chunks: int,
    document_metadata: DocumentMetadata,
    chunk_size: int,
    section: Optional[str] = None
) -> ChunkMetadata:
    """
    Create metadata for a document chunk.
    
    Args:
        chunk_id: Unique chunk identifier
        chunk_index: Position in document (0-based)
        total_chunks: Total chunks in document
        document_metadata: Parent document metadata
        chunk_size: Size in characters
        section: Optional section name
    
    Returns:
        ChunkMetadata object
    """
    return ChunkMetadata(
        chunk_id=chunk_id,
        chunk_index=chunk_index,
        total_chunks=total_chunks,
        document_source_path=document_metadata.source_path,
        document_category=document_metadata.category,
        chunk_size=chunk_size,
        section=section
    )


def _extract_section(chunk_text: str, full_content: str, start_pos: int) -> Optional[str]:
    """Extract section/heading name from chunk context."""
    # Look for the most recent heading before this chunk
    lines_before = full_content[:start_pos].split('\n')
    
    # Search backwards for headings
    for line in reversed(lines_before):
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        elif line.startswith('## '):
            return line[3:].strip()
        elif line.startswith('### '):
            return line[4:].strip()
    
    return None


def merge_for_vector_store(
    doc_metadata: DocumentMetadata,
    chunk_metadata: ChunkMetadata
) -> Dict[str, Any]:
    """
    Merge document and chunk metadata into a flat dict for vector store.
    
    Args:
        doc_metadata: Document metadata
        chunk_metadata: Chunk metadata
    
    Returns:
        Dictionary ready for vector store
    """
    return {
        'source_path': doc_metadata.source_path,
        'filename': doc_metadata.filename,
        'category': doc_metadata.category.value,
        'title': doc_metadata.title,
        'chunk_id': chunk_metadata.chunk_id,
        'chunk_index': chunk_metadata.chunk_index,
        'section': chunk_metadata.section,
    }
