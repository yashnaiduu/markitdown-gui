from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

from services.converter import ConverterService
from services.rag_pipeline import RAGPipeline
from services.ollama_client import OllamaClient
from storage.knowledge_base import KnowledgeBaseManager

app = FastAPI(title="MarkItDown Studio Backend API")

# Initialize services
converter = ConverterService()
ollama = OllamaClient()

# Request Models
class ConvertRequest(BaseModel):
    source_type: str  # "file", "url", or "youtube"
    source: str       # file path or URL

class IndexRequest(BaseModel):
    file_path: str
    document_id: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    prompt: str
    history: List[ChatMessage]
    use_rag: bool = False

@app.on_event("startup")
def startup_event():
    # Setup directories
    KnowledgeBaseManager.setup_directories()

@app.post("/api/convert")
def convert_source(request: ConvertRequest):
    try:
        if request.source_type == "file":
            path = converter.convert_local_file(request.source)
        elif request.source_type == "youtube":
            path = converter.convert_youtube(request.source)
        else:
            path = converter.convert_url(request.source)
            
        if path:
            return {"status": "success", "file_path": str(path), "name": path.name}
        raise HTTPException(status_code=500, detail="Conversion returned None")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/kb/index")
def index_document(request: IndexRequest):
    try:
        chunks_indexed = RAGPipeline.index_document(request.file_path, request.document_id)
        return {"status": "success", "chunks_indexed": chunks_indexed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/kb/list")
def list_documents():
    try:
        docs = KnowledgeBaseManager.get_all_documents()
        return {"status": "success", "documents": [{"name": d.name, "path": str(d)} for d in docs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/kb/delete")
def delete_document(file_path: str):
    from pathlib import Path
    try:
        success = KnowledgeBaseManager.delete_document(Path(file_path))
        return {"status": "success", "deleted": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        context = ""
        if request.use_rag:
            context = RAGPipeline.retrieve_context(request.prompt)
            
        # Convert Pydantic models to dicts for OllamaClient
        history_dicts = [{"role": m.role, "content": m.content} for m in request.history]
        
        # Note: We are using generate() instead of stream() because streaming 
        # over standard HTTP requires Server-Sent Events (SSE). For simplicity
        # in the native API bridge, we will return the full response.
        response = ollama.generate(
            prompt=request.prompt,
            context=context if context else None,
            history=history_dicts
        )
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)
