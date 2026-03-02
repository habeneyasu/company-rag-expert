"""
Prompt management for RAG generation.

This module handles building prompts with retrieved context for LLM generation.
"""

from typing import List, Dict, Any, Optional


class PromptBuilder:
    """Builder for RAG prompts with context."""
    
    DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful assistant that answers questions based on the provided context "
        "from company documents. If the context doesn't contain enough information to answer "
        "the question, say so."
    )
    
    DEFAULT_TEMPLATE = "Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        template: Optional[str] = None
    ):
        """
        Initialize prompt builder.
        
        Args:
            system_prompt: System prompt for LLM
            template: Prompt template with {context} and {query} placeholders
        """
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.template = template or self.DEFAULT_TEMPLATE
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context string.
        
        Args:
            results: List of search results with 'text' and 'metadata' keys
        
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            doc_title = metadata.get('document_title') or metadata.get('document_filename', 'Unknown')
            section = metadata.get('section')
            
            source_info = f"[{i}]"
            if section:
                source_info += f" Section: {section}"
            source_info += f" (Source: {doc_title})"
            
            context_parts.append(f"{source_info}\n{text}")
        
        return "\n\n".join(context_parts)
    
    def build_prompt(
        self,
        query: str,
        results: List[Dict[str, Any]],
        max_context_chunks: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Build complete prompt with context.
        
        Args:
            query: User query
            results: Search results to use as context
            max_context_chunks: Maximum number of chunks to include
        
        Returns:
            Dict with 'system' and 'user' prompt strings
        """
        context_results = results[:max_context_chunks] if max_context_chunks else results
        context = self.format_context(context_results)
        
        return {
            'system': self.system_prompt,
            'user': self.template.format(context=context, query=query)
        }
