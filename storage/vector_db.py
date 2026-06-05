import chromadb
from chromadb.config import Settings
from core.config import KB_CHROMA_DIR
from storage.knowledge_base import KnowledgeBaseManager


class VectorDBManager:
    """Manages the persistent ChromaDB local vector store.
    
    Uses lazy initialization — the database connection is only created
    when first needed, not at import time. This prevents crashes on macOS
    when the Documents folder permission hasn't been granted yet.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDBManager, cls).__new__(cls)
        return cls._instance
        
    def _ensure_initialized(self):
        """Lazily initialize the database connection on first use."""
        if self._initialized:
            return
            
        # Ensure directories exist before ChromaDB tries to write
        KnowledgeBaseManager.setup_directories()
        
        # Import here to avoid circular imports at module level
        from services.embeddings import EmbeddingsService
        
        self.client = chromadb.PersistentClient(
            path=str(KB_CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Custom embedding function adapter for Chroma
        class CustomEmbeddingFunction:
            def __init__(self):
                self.embedder = EmbeddingsService()
            def __call__(self, input: list[str]) -> list[list[float]]:
                return self.embedder.get_embeddings(input)
                
        self.embedding_function = CustomEmbeddingFunction()
        
        # Get or create the main collection
        self.collection = self.client.get_or_create_collection(
            name="markitdown_studio",
            embedding_function=self.embedding_function
        )
        self._initialized = True
        
    def add_chunks(self, document_id: str, chunks: list[str], metadata: dict = None):
        """Add text chunks from a document to the vector database."""
        self._ensure_initialized()
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [metadata or {"source_id": document_id} for _ in chunks]
        
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
    def search(self, query: str, n_results: int = 5):
        """Semantic search against the vector database."""
        self._ensure_initialized()
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def delete_document(self, document_id: str):
        """Delete all chunks for a specific document."""
        self._ensure_initialized()
        self.collection.delete(
            where={"source_id": document_id}
        )


def get_vector_db() -> VectorDBManager:
    """Get the VectorDBManager singleton. Use this instead of a module-level instance."""
    return VectorDBManager()
