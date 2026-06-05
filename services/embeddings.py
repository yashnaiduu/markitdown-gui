from sentence_transformers import SentenceTransformer
from core.config import settings

class EmbeddingsService:
    """Handles generating embeddings locally using sentence-transformers."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingsService, cls).__new__(cls)
        return cls._instance
        
    def _load_model(self):
        if self._model is None:
            model_name = settings.embedding_model
            # Model will be downloaded if not present, then cached locally.
            self._model = SentenceTransformer(model_name)
            
    def get_embedding(self, text: str) -> list[float]:
        self._load_model()
        embedding = self._model.encode(text)
        return embedding.tolist()
        
    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        self._load_model()
        embeddings = self._model.encode(texts)
        return embeddings.tolist()
