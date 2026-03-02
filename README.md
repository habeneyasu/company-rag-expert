# Company RAG Expert

A Retrieval-Augmented Generation (RAG) system for company knowledge base management. Ingests documents, creates vector embeddings, and enables semantic search for intelligent question-answering.

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

## Features

- **Document Ingestion**: Automatic loading and metadata extraction from markdown documents
- **Intelligent Chunking**: Context-aware document splitting with overlap and section detection
- **Vector Storage**: Local ChromaDB persistence for embeddings (no external services required)
- **Semantic Search**: Embedding-based similarity search for relevant document chunks
- **Result Reranking**: Cross-encoder models for improved search relevance
- **RAG Pipeline**: Complete pipeline ready for LLM integration

## Quick Start

```bash
pip install -r requirements.txt
```

### Ingest Documents

```python
from src.core.knowledge_service import ingest_knowledge_base
from pathlib import Path

stats = ingest_knowledge_base(vector_store_path=Path("data/chroma_db"))
```

### Search and Rerank

```python
from src.retrieval.search import SearchEngine
from src.retrieval.reranker import Reranker

engine = SearchEngine()
results = engine.search("What is the company policy?", n_results=10)
reranked = Reranker().rerank("What is the company policy?", results, top_k=5)
```

## Knowledge Base Structure

Documents are organized by category in the `knowledge-base/` directory:
- `company/` - Company policies and organizational information
- `contracts/` - Legal templates and agreements
- `employees/` - Employee-facing documents
- `products/` - Product documentation and specifications

## Requirements

Python 3.8+. See `requirements.txt` for dependencies.

## License

MIT
