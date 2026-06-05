from core.config import settings


class RAGPipeline:
    """Orchestrates chunking, indexing, and context retrieval."""
    
    @staticmethod
    def _get_db():
        """Lazy import to avoid triggering ChromaDB init at import time."""
        from storage.vector_db import get_vector_db
        return get_vector_db()
    
    @staticmethod
    def chunk_markdown(text: str, chunk_size: int = None, chunk_overlap: int = None) -> list[str]:
        """Simple character-based chunking with overlap."""
        c_size = chunk_size or settings.chunk_size
        c_overlap = chunk_overlap or settings.chunk_overlap
        
        # Split by double newline first to preserve paragraphs where possible
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for p in paragraphs:
            if len(current_chunk) + len(p) < c_size:
                current_chunk += p + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # Handle paragraphs larger than chunk size
                if len(p) > c_size:
                    for i in range(0, len(p), c_size - c_overlap):
                        chunks.append(p[i:i + c_size])
                    current_chunk = ""
                else:
                    current_chunk = p + "\n\n"
                    
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
        
    @staticmethod
    def index_document(file_path: str, document_id: str):
        """Read a markdown document, chunk it, and store in vector DB."""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        chunks = RAGPipeline.chunk_markdown(text)
        metadata = {"source_id": document_id, "file_path": file_path}
        
        db = RAGPipeline._get_db()
        db.add_chunks(document_id, chunks, metadata)
        return len(chunks)
        
    @staticmethod
    def retrieve_context(query: str, n_results: int = 3) -> str:
        """Retrieve relevant chunks for a query to be injected into prompt."""
        db = RAGPipeline._get_db()
        results = db.search(query, n_results=n_results)
        
        context_parts = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            for doc, meta in zip(docs, metas):
                source = meta.get("file_path", "Unknown Source")
                context_parts.append(f"--- SOURCE: {source} ---\n{doc}")
                
        return "\n\n".join(context_parts)
