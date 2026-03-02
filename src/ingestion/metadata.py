"""
Document-level metadata schema and utilities.

This module handles metadata extraction and management for complete documents.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class DocumentCategory(str, Enum):
    """Document categories."""
    COMPANY = "company"
    CONTRACTS = "contracts"
    EMPLOYEES = "employees"
    PRODUCTS = "products"


class DocumentMetadata(BaseModel):
    """Simple metadata schema for a document."""
    
    # Basic identification
    source_path: str = Field(..., description="Path to the document")
    filename: str = Field(..., description="Document filename")
    category: DocumentCategory = Field(..., description="Document category")
    
    # Document info
    title: Optional[str] = Field(None, description="Document title")
    document_owner: Optional[str] = Field(None, description="Document owner")
    version: Optional[str] = Field(None, description="Document version")
    last_updated: Optional[datetime] = Field(None, description="Last update date")
    
    # Processing info
    ingestion_date: datetime = Field(default_factory=datetime.now, description="When ingested")
    
    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


def extract_document_metadata(
    file_path: Path,
    content: Optional[str] = None
) -> DocumentMetadata:
    """
    Extract simple metadata from a document file.
    
    Args:
        file_path: Path to the document
        content: Optional document content
    
    Returns:
        DocumentMetadata object
    """
    file_path = Path(file_path)
    
    # Infer category from path
    category = _infer_category(file_path)
    
    # Extract basic info from content
    title = None
    owner = None
    version = None
    last_updated = None
    
    if content:
        lines = content.split('\n')
        # Get title from first heading
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # Look for metadata at the end
        for line in reversed(lines):
            line_lower = line.lower()
            if 'document owner' in line_lower:
                owner = _extract_value(line)
            elif 'version' in line_lower and ':' in line:
                version = _extract_value(line)
            elif 'last updated' in line_lower:
                date_str = _extract_value(line)
                if date_str:
                    last_updated = _parse_simple_date(date_str)
    
    return DocumentMetadata(
        source_path=str(file_path.absolute()),
        filename=file_path.name,
        category=category,
        title=title,
        document_owner=owner,
        version=version,
        last_updated=last_updated
    )


# Helper functions

def _infer_category(file_path: Path) -> DocumentCategory:
    """Infer category from file path."""
    path_str = str(file_path).lower()
    if "company" in path_str:
        return DocumentCategory.COMPANY
    elif "contract" in path_str:
        return DocumentCategory.CONTRACTS
    elif "employee" in path_str:
        return DocumentCategory.EMPLOYEES
    elif "product" in path_str:
        return DocumentCategory.PRODUCTS
    return DocumentCategory.COMPANY  # default


def _extract_value(line: str) -> Optional[str]:
    """Extract value from 'key: value' format."""
    line = line.replace('**', '').strip()
    if ':' in line:
        return line.split(':', 1)[1].strip()
    return None


def _parse_simple_date(date_str: str) -> Optional[datetime]:
    """Parse common date formats."""
    date_str = date_str.strip()
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None
