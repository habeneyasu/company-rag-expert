"""Gradio chat interface for the RAG system."""

from pathlib import Path
from typing import List, Dict, Any

try:
    import gradio as gr
except ImportError:
    raise ImportError(
        "gradio is required. Install with: uv pip install gradio"
    )

from ..core.knowledge_service import KnowledgeService, ingest_knowledge_base
from ..storage.vector_store import VectorStore


def create_chat_fn(vector_store_path: Path, use_reranker: bool = True):
    """Create chat function for ChatInterface."""
    vector_store = VectorStore(persist_directory=vector_store_path)
    
    # Auto-ingest if vector store is empty
    try:
        stats = vector_store.get_collection_stats()
        if stats['total_chunks'] == 0:
            ingest_knowledge_base(vector_store_path=vector_store_path, show_progress=False)
    except Exception:
        ingest_knowledge_base(vector_store_path=vector_store_path, show_progress=False)
    
    service = KnowledgeService(
        vector_store=vector_store,
        use_reranker=use_reranker
    )
    
    def chat(message: str, history: List[List[str]]) -> str:
        """Chat function that processes messages and returns responses."""
        if not message.strip():
            return ""
        
        try:
            result = service.query(message, n_results=10, top_k=5)
            return result['answer']
        except Exception as e:
            return f"Error: {str(e)}"
    
    return chat


def launch_app(
    vector_store_path: Path = Path("data/chroma_db"),
    use_reranker: bool = True,
    share: bool = False,
    server_name: str = "127.0.0.1",
    server_port: int = 7860
):
    chat_fn = create_chat_fn(vector_store_path, use_reranker)
    
    def respond(message, history):
        if not message.strip():
            return "", history
        
        history_list = []
        for item in history:
            if isinstance(item, dict):
                if item.get("role") == "user":
                    history_list.append([item.get("content", ""), None])
                elif item.get("role") == "assistant":
                    if history_list:
                        history_list[-1][1] = item.get("content", "")
            elif isinstance(item, list) and len(item) == 2:
                history_list.append(item)
        
        history_list.append([message, None])
        
        gradio_history = []
        for user_msg, bot_msg in history_list[:-1]:
            gradio_history.append({"role": "user", "content": user_msg})
            if bot_msg:
                gradio_history.append({"role": "assistant", "content": bot_msg})
        
        gradio_history.append({"role": "user", "content": message})
        loading_spinner = '<div style="display: flex; align-items: center; gap: 8px;"><div style="border: 2px solid #e0e0e0; border-top: 2px solid #3498db; border-radius: 50%; width: 16px; height: 16px; animation: spin 0.8s linear infinite; display: inline-block;"></div><span>Processing...</span></div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>'
        gradio_history.append({"role": "assistant", "content": loading_spinner})
        yield "", gradio_history
        
        try:
            response = chat_fn(message, history_list[:-1])
            gradio_history[-1] = {"role": "assistant", "content": response}
            yield "", gradio_history
        except Exception as e:
            gradio_history[-1] = {"role": "assistant", "content": f"Error: {str(e)}"}
            yield "", gradio_history
    
    theme = gr.themes.Soft(font=["Inter", "system-ui", "sans-serif"])
    
    with gr.Blocks(title="Company RAG Expert", theme=theme) as app:
        gr.Markdown("# Company RAG Expert\n**Intelligent Knowledge Base Assistant**")
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500
                )
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask a question about your company knowledge base...",
                        show_label=False,
                        scale=9,
                        container=False
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### About\n\nAsk questions about your company policies, documentation, and knowledge base. The system will search through your documents and provide context-aware answers.")
                
                with gr.Accordion("How it works", open=False):
                    gr.Markdown("""
                    1. **Ingest**: Documents are loaded and chunked
                    2. **Embed**: Chunks are converted to vector embeddings
                    3. **Search**: Semantic search finds relevant content
                    4. **Rerank**: Results are reordered for relevance
                    5. **Generate**: LLM synthesizes the final answer
                    """)
        
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        submit_btn.click(respond, [msg, chatbot], [msg, chatbot])
        clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])
    
    app.launch(share=share, server_name=server_name, server_port=server_port)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch Gradio interface for RAG system")
    parser.add_argument(
        "--vector-store",
        type=Path,
        default=Path("data/chroma_db"),
        help="Path to vector store directory"
    )
    parser.add_argument(
        "--no-reranker",
        action="store_true",
        help="Disable reranker"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create public link"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Server port"
    )
    
    args = parser.parse_args()
    
    launch_app(
        vector_store_path=args.vector_store,
        use_reranker=not args.no_reranker,
        share=args.share,
        server_port=args.port
    )


if __name__ == "__main__":
    main()
