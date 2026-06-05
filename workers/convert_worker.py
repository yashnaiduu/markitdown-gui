import traceback
from PySide6.QtCore import QRunnable, QObject, Signal
from services.converter import ConverterService

class ConvertWorkerSignals(QObject):
    finished = Signal(object) # Path object of the saved file
    error = Signal(str)

class ConvertWorker(QRunnable):
    """Background worker for converting files/URLs."""
    
    def __init__(self, source: str, source_type: str = "file", dest_dir: str | None = None):
        super().__init__()
        self.source = source
        self.source_type = source_type
        self.dest_dir = dest_dir
        self.signals = ConvertWorkerSignals()
        self.converter = ConverterService()
        
    def run(self):
        try:
            if self.source_type == "file":
                from pathlib import Path
                d_dir = Path(self.dest_dir) if self.dest_dir else None
                result_path = self.converter.convert_local_file(self.source, dest_dir=d_dir)
            elif self.source_type == "url":
                result_path = self.converter.convert_url(self.source)
            elif self.source_type == "youtube":
                result_path = self.converter.convert_youtube(self.source)
            else:
                raise ValueError(f"Unknown source type: {self.source_type}")
                
            self.signals.finished.emit(result_path)

            
        except Exception as e:
            err_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.signals.error.emit(err_msg)
