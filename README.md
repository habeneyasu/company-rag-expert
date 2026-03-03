# Company RAG Expert

**Turn your static documents into a conversational AI.**

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LLM](https://img.shields.io/badge/LLM-OpenRouter-green)](https://openrouter.ai/)

## The Problem

Your company knowledge is scattered across countless documents—policy PDFs, engineering wikis, legal templates, and technical documentation. Finding the right information means digging through folders, searching through files, and hoping you stumble upon the right document. It's time-consuming, frustrating, and inefficient.

## The Solution

Company RAG Expert transforms your static documents into an intelligent, conversational assistant. Simply ask a question in plain English, and get precise, context-aware answers grounded in your company's knowledge base. No more folder diving. No more keyword guessing. Just ask and get answers.

![Gradio Chat Interface - Company Policy](assets/Company%20Policy.png)

*Ask questions in plain English; get answers grounded in your company's documents.*

![Gradio Chat Interface - Company Core Values](assets/Company%20Core%20Values.png)

*Query any aspect of your knowledge base—from policies to values to technical documentation.*

## What You Get

**Instant Answers**: Ask questions about your company policies, documentation, or knowledge base and get immediate, accurate responses.

**Smart Understanding**: The system understands the meaning behind your questions, not just keyword matching. Ask "What's our remote work policy?" and get the exact information you need.

**Automatic Processing**: Just drop your markdown files into the knowledge base folder. The system automatically processes, organizes, and makes them searchable.

**Privacy-First**: Your documents stay on your machine. Only the final answer generation uses an external service—your data never leaves your control.

**Easy to Use**: A clean, web-based interface that anyone can use. No technical expertise required to ask questions or get answers.

**Always Up-to-Date**: Add new documents anytime. The system automatically incorporates them into the knowledge base.

## How It Works (Simple Version)

1. You add your documents to the knowledge base folder
2. The system processes and understands your documents
3. You ask a question in natural language
4. The system finds the most relevant information from your documents
5. You get a clear, accurate answer based on your company's knowledge

That's it. No complex setup. No technical configuration. Just add documents and start asking questions.

## Getting Started

### What You Need

- Python 3.9 or higher installed on your computer
- An [OpenRouter API Key](https://openrouter.ai/keys) (free tier available)

### Step-by-Step Setup

**1. Get the code**

```bash
git clone https://github.com/habeneyasu/company-rag-expert.git
cd company-rag-expert
```

**2. Install the software**

**Option A: Using uv (recommended for faster installation)**

```bash
# Install uv package manager (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv && source .venv/bin/activate && uv pip install torch --index-url https://download.pytorch.org/whl/cpu && uv pip install -r requirements.txt
```

**Option B: Using standard pip**

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install PyTorch (CPU version)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
pip install -r requirements.txt
```

**3. Set up your API key**

Create a `.env` file in the project folder and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_api_key_here
```

**4. Add your documents**

Place your markdown files into the `knowledge-base/` folder. Organize them however makes sense for your company:
- Company policies
- Employee handbooks
- Technical documentation
- Legal templates
- Product information

**5. Start the application**

```bash
python -m src.ui.gradio_app --vector-store data/chroma_db
```

The system will automatically process your documents the first time you run it. Then open your browser to `http://localhost:7860` and start asking questions!

## Real-World Examples

**Employee Onboarding**: New hires can ask "What's the process for setting up my development environment?" and get step-by-step instructions instantly.

**Sales & Support**: Sales representatives can ask "What are the compliance certifications for Enterprise tier?" during customer calls and get accurate, up-to-date information in real-time.

**Policy Questions**: Employees can ask "How many vacation days do I accrue per year?" and receive the exact policy information with relevant context.

**Technical Help**: Developers can query API documentation, technical specifications, and troubleshooting guides using natural language instead of searching through multiple files.

## Frequently Asked Questions

**Q: What file formats are supported?**  
A: Currently, the system works with markdown (.md) files. This keeps things simple and ensures your documents are easy to edit and maintain.

**Q: Do I need to be a programmer to use this?**  
A: Not at all! Once set up, anyone can use the web interface to ask questions. The setup process requires basic command-line knowledge, but using the system is as simple as typing a question.

**Q: Is my data secure?**  
A: Yes. Your documents are stored locally on your machine. Only when generating answers does the system send a query (not your documents) to an external LLM service.

**Q: Can I add new documents later?**  
A: Absolutely! Just add new markdown files to your knowledge base folder and restart the application. The system will automatically process the new documents.

**Q: What if I want to customize how it works?**  
A: The system works great out of the box with sensible defaults. For advanced customization of chunk sizes, search parameters, or model selection, you can modify the `KnowledgeService` initialization in your code. Check the source code in `src/core/knowledge_service.py` for available options.

## Contributing

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, your help makes this project better for everyone. Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.
