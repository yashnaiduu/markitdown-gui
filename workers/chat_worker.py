import traceback
from PySide6.QtCore import QRunnable, QObject, Signal
from services.ollama_client import OllamaClient
from services.rag_pipeline import RAGPipeline

class ChatWorkerSignals(QObject):
    chunk_received = Signal(str)
    finished = Signal()
    error = Signal(str)

class ChatWorker(QRunnable):
    """Background worker for streaming Ollama responses."""
    
    def __init__(self, prompt: str, history: list[dict], use_rag: bool = False):
        super().__init__()
        self.prompt = prompt
        self.history = history
        self.use_rag = use_rag
        self.signals = ChatWorkerSignals()
        self.client = OllamaClient()
        
    def run(self):
        try:
            # If RAG is enabled, retrieve context and inject it
            if self.use_rag:
                context = RAGPipeline.retrieve_context(self.prompt)
                augmented_prompt = (
                    f"Use the following context to answer the user's question. "
                    f"If the context doesn't contain the answer, say so.\n\n"
                    f"Context:\n{context}\n\n"
                    f"Question: {self.prompt}"
                )
                self.history.append({"role": "user", "content": augmented_prompt})
            else:
                self.history.append({"role": "user", "content": self.prompt})

            # Stream response
            stream = self.client.chat_stream(self.history)
            
            full_response = ""
            for chunk in stream:
                full_response += chunk
                self.signals.chunk_received.emit(chunk)
                
            self.history.append({"role": "assistant", "content": full_response})
            self.signals.finished.emit()
            
        except Exception as e:
            err_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.signals.error.emit(err_msg)
