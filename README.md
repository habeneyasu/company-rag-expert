# Company RAG Expert

A Retrieval-Augmented Generation (RAG) system for company knowledge base management.

## Overview

This system ingests company documents, creates vector embeddings, and enables semantic search for intelligent question-answering.

## Architecture

```
src/
├── ingestion/      # Document loading, metadata extraction, chunking
├── storage/        # Embeddings generation and vector store (ChromaDB)
├── retrieval/      # Search and reranking
├── generation/     # LLM integration and prompt management
├── core/           # Knowledge service orchestrator
├── api/            # FastAPI endpoints
└── ui/             # Streamlit interface
```

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Ingest Knowledge Base

```python
from src.core.knowledge_service import ingest_knowledge_base
from pathlib import Path

# Ingest documents (defaults to knowledge-base directory)
stats = ingest_knowledge_base(
    vector_store_path=Path("data/chroma_db")  # Optional: persist to disk
)

print(f"Processed {stats['documents_processed']} documents")
print(f"Created {stats['total_chunks']} chunks")
```

## Features

- **Document Ingestion**: Load markdown documents with automatic metadata extraction
- **Intelligent Chunking**: Split documents with overlap and section detection
- **Vector Storage**: ChromaDB for local persistence (no external services needed)
- **Semantic Search**: Find relevant chunks using embeddings
- **RAG Pipeline**: Ready for LLM integration

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Usage

```python
from src.core.knowledge_service import KnowledgeService, ingest_knowledge_base
from pathlib import Path

# Option 1: Use convenience function
stats = ingest_knowledge_base(
    vector_store_path=Path("data/chroma_db")
)

# Option 2: Use service class directly
from src.storage.vector_store import VectorStore

service = KnowledgeService(
    vector_store=VectorStore(persist_directory=Path("data/chroma_db")),
    chunk_size=1000,
    chunk_overlap=200
)
stats = service.ingest()
```

## Knowledge Base Structure

Documents are organized by category:
- `company/` - Company policies and organizational info
- `contracts/` - Legal templates and agreements
- `employees/` - Employee-facing documents
- `products/` - Product documentation and specs

## License

MIT
