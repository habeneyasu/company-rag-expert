"""
Document chunking and chunk metadata.

This module handles splitting documents into chunks and creating metadata for each chunk.
"""

from datetime import datetime
from typing import List, Optional, Tuple, TYPE_CHECKING
from pydantic import BaseModel, Field
from .metadata import DocumentCategory  # Needed at runtime for ChunkMetadata

if TYPE_CHECKING:
    from .metadata import DocumentMetadata


class ChunkMetadata(BaseModel):
    """Metadata schema for a document chunk."""
    
    # Chunk identification
    chunk_id: str = Field(..., description="Unique chunk identifier")
    chunk_index: int = Field(..., description="Chunk position in document (0-based)")
    total_chunks: int = Field(..., description="Total number of chunks")
    
    # Reference to parent document
    document_source_path: str = Field(..., description="Source document path")
    document_filename: str = Field(..., description="Document filename")
    document_category: DocumentCategory = Field(..., description="Document category")
    document_title: Optional[str] = Field(None, description="Document title")
    document_version: Optional[str] = Field(None, description="Document version")
    document_owner: Optional[str] = Field(None, description="Document owner")
    document_last_updated: Optional[datetime] = Field(None, description="Document last update date")
    document_ingestion_date: datetime = Field(..., description="When document was ingested")
    
    # Chunk info
    section: Optional[str] = Field(None, description="Section name")
    chunk_size: int = Field(..., description="Chunk size in characters")
    
    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


def _create_chunk_metadata(
    document_metadata,  # DocumentMetadata (imported only for type checking)
    chunk_index: int,
    chunk_text: str,
    section: Optional[str],
    total_chunks: int = 0
) -> ChunkMetadata:
    """Create ChunkMetadata from DocumentMetadata."""
    return ChunkMetadata(
        chunk_id=f"{document_metadata.filename}_chunk_{chunk_index}",
        chunk_index=chunk_index,
        total_chunks=total_chunks,
        document_source_path=document_metadata.source_path,
        document_filename=document_metadata.filename,
        document_category=document_metadata.category,
        document_title=document_metadata.title,
        document_version=document_metadata.version,
        document_owner=document_metadata.document_owner,
        document_last_updated=document_metadata.last_updated,
        document_ingestion_date=document_metadata.ingestion_date,
        chunk_size=len(chunk_text),
        section=section
    )


def chunk_document(
    content: str,
    document_metadata,  # DocumentMetadata (received from loader via knowledge_service)
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
    start = 0
    chunk_index = 0
    
    while start < content_length:
        end = min(start + chunk_size, content_length)
        chunk_text = content[start:end]
        section = _extract_section(chunk_text, content, start)
        
        chunk_meta = _create_chunk_metadata(
            document_metadata, chunk_index, chunk_text, section
        )
        chunks.append((chunk_text, chunk_meta))
        
        start = end - chunk_overlap if end < content_length else end
        chunk_index += 1
    
    # Update total_chunks in all metadata
    for _, chunk_meta in chunks:
        chunk_meta.total_chunks = len(chunks)
    
    return chunks


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
