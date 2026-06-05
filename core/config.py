import os
from pathlib import Path
from PySide6.QtCore import QSettings

APP_NAME = "MarkItDown Studio"
APP_VERSION = "1.0.0"

# User-specific application data directory
USER_DATA_DIR = Path.home() / "Documents" / APP_NAME

# Knowledge base directories
KNOWLEDGE_BASE_DIR = USER_DATA_DIR / "knowledge_base"
KB_MARKDOWN_DIR = KNOWLEDGE_BASE_DIR / "markdown"
KB_URLS_DIR = KNOWLEDGE_BASE_DIR / "urls"
KB_YOUTUBE_DIR = KNOWLEDGE_BASE_DIR / "youtube"
KB_UPLOADS_DIR = KNOWLEDGE_BASE_DIR / "uploads"
KB_CHROMA_DIR = KNOWLEDGE_BASE_DIR / "chroma"
KB_EMBEDDINGS_DIR = KNOWLEDGE_BASE_DIR / "embeddings"
KB_LOGS_DIR = KNOWLEDGE_BASE_DIR / "logs"
KB_EXPORTS_DIR = KNOWLEDGE_BASE_DIR / "exports"

# AI Defaults
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_OLLAMA_MODEL = "llama3"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

# Settings Helper
class AppSettings:
    """Helper to manage QSettings."""
    
    def __init__(self):
        self._settings = QSettings("MarkItDown", APP_NAME)
        
    @property
    def offline_mode(self) -> bool:
        # Default is True (ON) as per spec
        return self._settings.value("privacy/offline_mode", True, type=bool)
        
    @offline_mode.setter
    def offline_mode(self, value: bool):
        self._settings.setValue("privacy/offline_mode", value)

    @property
    def auto_index(self) -> bool:
        return self._settings.value("privacy/auto_index", True, type=bool)
        
    @auto_index.setter
    def auto_index(self, value: bool):
        self._settings.setValue("privacy/auto_index", value)

    @property
    def output_destination(self) -> str:
        return self._settings.value("export/output_destination", "kb", type=str)

    @output_destination.setter
    def output_destination(self, value: str):
        self._settings.setValue("export/output_destination", value)

    @property
    def custom_output_path(self) -> str:
        return self._settings.value("export/custom_output_path", str(USER_DATA_DIR / "exports"), type=str)

    @custom_output_path.setter
    def custom_output_path(self, value: str):
        self._settings.setValue("export/custom_output_path", value)

    @property
    def embedding_model(self) -> str:
        return self._settings.value("ai/embedding_model", DEFAULT_EMBEDDING_MODEL, type=str)
        
    @embedding_model.setter
    def embedding_model(self, value: str):
        self._settings.setValue("ai/embedding_model", value)

    @property
    def ollama_model(self) -> str:
        return self._settings.value("ai/ollama_model", DEFAULT_OLLAMA_MODEL, type=str)
        
    @ollama_model.setter
    def ollama_model(self, value: str):
        self._settings.setValue("ai/ollama_model", value)

    @property
    def chunk_size(self) -> int:
        return self._settings.value("rag/chunk_size", DEFAULT_CHUNK_SIZE, type=int)
        
    @chunk_size.setter
    def chunk_size(self, value: int):
        self._settings.setValue("rag/chunk_size", value)

    @property
    def chunk_overlap(self) -> int:
        return self._settings.value("rag/chunk_overlap", DEFAULT_CHUNK_OVERLAP, type=int)
        
    @chunk_overlap.setter
    def chunk_overlap(self, value: int):
        self._settings.setValue("rag/chunk_overlap", value)

settings = AppSettings()

