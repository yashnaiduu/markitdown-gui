from pathlib import Path
from typing import Optional
from markitdown import MarkItDown
from core.security.network_guard import network_guard
from storage.knowledge_base import KnowledgeBaseManager

class ConverterService:
    """Service to handle document and URL conversions to Markdown."""
    
    def __init__(self):
        try:
            from openai import OpenAI
            # Point OpenAI client to local Ollama instance
            client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            self.md = MarkItDown(
                enable_plugins=True,
                llm_client=client,
                llm_model="llava"  # Default Ollama vision model
            )
        except Exception as e:
            print(f"Failed to initialize MarkItDown with LLM OCR: {e}")
            self.md = MarkItDown()
        
    def convert_local_file(self, file_path: str, dest_dir: Path = None) -> Optional[Path]:
        """Convert a local file to markdown and save it to the target directory."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        result = self.md.convert(file_path)
        content = result.text_content
        
        filename = f"{path.stem}.md"
        if dest_dir:
            dest_dir.mkdir(parents=True, exist_ok=True)
            saved_path = dest_dir / filename
            counter = 1
            while saved_path.exists():
                new_name = f"{path.stem}_{counter}.md"
                saved_path = dest_dir / new_name
                counter += 1
            with open(saved_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            saved_path = KnowledgeBaseManager.save_markdown(content, filename, source_type="markdown")
        return saved_path

        
    def convert_url(self, url: str) -> Optional[Path]:
        """Convert a web URL to markdown."""
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        
        # Guard network request
        network_guard.check(parsed.hostname, require_user_intent=True)
        
        result = self.md.convert(url)
        content = f"# Source: {url}\n\n{result.text_content}"
        
        # Create a safe filename from URL
        safe_name = parsed.hostname + parsed.path.replace('/', '_')
        if not safe_name.endswith('.md'):
            safe_name += '.md'
            
        saved_path = KnowledgeBaseManager.save_markdown(content, safe_name, source_type="urls")
        return saved_path

    def convert_youtube(self, url: str) -> Optional[Path]:
        """Convert a YouTube video transcript to markdown."""
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        
        # Guard network request
        network_guard.check(parsed.hostname, require_user_intent=True)
        
        try:
            # First try using MarkItDown directly
            result = self.md.convert(url)
            content = f"# Source: {url}\n\n{result.text_content}"
        except Exception:
            # Fallback to youtube-transcript-api if MarkItDown fails for YT
            from youtube_transcript_api import YouTubeTranscriptApi
            video_id = None
            if "v=" in url:
                video_id = urllib.parse.parse_qs(parsed.query).get("v", [None])[0]
            elif "youtu.be" in url:
                video_id = parsed.path.lstrip('/')
                
            if not video_id:
                raise ValueError("Could not extract YouTube video ID.")
                
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text_lines = [item['text'] for item in transcript]
            content = f"# Source: {url}\n\n" + "\n".join(text_lines)
            
        filename = f"youtube_{parsed.hostname}.md"
        saved_path = KnowledgeBaseManager.save_markdown(content, filename, source_type="youtube")
        return saved_path
