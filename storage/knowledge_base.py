import os
import shutil
from pathlib import Path
from core.config import (
    KNOWLEDGE_BASE_DIR,
    KB_MARKDOWN_DIR,
    KB_URLS_DIR,
    KB_YOUTUBE_DIR,
    KB_UPLOADS_DIR,
    KB_CHROMA_DIR,
    KB_EMBEDDINGS_DIR,
    KB_LOGS_DIR,
    KB_EXPORTS_DIR
)

class KnowledgeBaseManager:
    """Manages the local knowledge base file system."""
    
    @staticmethod
    def setup_directories():
        """Creates the necessary directory structure."""
        dirs = [
            KNOWLEDGE_BASE_DIR,
            KB_MARKDOWN_DIR,
            KB_URLS_DIR,
            KB_YOUTUBE_DIR,
            KB_UPLOADS_DIR,
            KB_CHROMA_DIR,
            KB_EMBEDDINGS_DIR,
            KB_LOGS_DIR,
            KB_EXPORTS_DIR
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            
    @staticmethod
    def get_all_documents():
        """Returns a list of all markdown documents in the knowledge base."""
        # Check markdown, urls, youtube, uploads directories
        docs = []
        search_dirs = [KB_MARKDOWN_DIR, KB_URLS_DIR, KB_YOUTUBE_DIR, KB_UPLOADS_DIR]
        
        for d in search_dirs:
            if d.exists():
                docs.extend(list(d.glob("**/*.md")))
        return docs
        
    @staticmethod
    def save_markdown(content: str, filename: str, source_type: str = "markdown") -> Path:
        """
        Save markdown content to the appropriate folder.
        source_type can be 'markdown', 'urls', 'youtube', 'uploads'
        """
        KnowledgeBaseManager.setup_directories()
        
        target_dir = KNOWLEDGE_BASE_DIR / source_type
        if not target_dir.exists():
            target_dir = KB_MARKDOWN_DIR
            
        file_path = target_dir / filename
        
        # Handle duplicate filenames
        counter = 1
        while file_path.exists():
            base = file_path.stem
            ext = file_path.suffix
            # Remove previous counter if exists, simplistically
            if "_" in base and base.split("_")[-1].isdigit():
                base = "_".join(base.split("_")[:-1])
            new_name = f"{base}_{counter}{ext}"
            file_path = target_dir / new_name
            counter += 1
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return file_path

    @staticmethod
    def delete_document(file_path: Path):
        """Deletes a document from the knowledge base."""
        if file_path.exists() and file_path.is_file():
            # Ensure it's within the KB
            if KNOWLEDGE_BASE_DIR in file_path.parents:
                try:
                    from storage.vector_db import get_vector_db
                    get_vector_db().delete_document(file_path.name)
                except Exception as e:
                    print(f"Failed to delete {file_path.name} from vector DB: {e}")
                
                file_path.unlink()
                return True
        return False

