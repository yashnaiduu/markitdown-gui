import traceback
from PySide6.QtCore import QRunnable, QObject, Signal
from services.rag_pipeline import RAGPipeline

class IndexWorkerSignals(QObject):
    finished = Signal(int) # Number of chunks indexed
    error = Signal(str)

class IndexWorker(QRunnable):
    """Background worker for indexing markdown files into Vector DB."""
    
    def __init__(self, file_path: str, document_id: str):
        super().__init__()
        self.file_path = file_path
        self.document_id = document_id
        self.signals = IndexWorkerSignals()
        
    def run(self):
        try:
            chunks_count = RAGPipeline.index_document(self.file_path, self.document_id)
            self.signals.finished.emit(chunks_count)
        except Exception as e:
            err_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.signals.error.emit(err_msg)
