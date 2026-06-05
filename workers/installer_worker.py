import sys
import subprocess
from PySide6.QtCore import QThread, Signal

class InstallerWorker(QThread):
    """
    Background worker to install the 'markitdown[all]' dependency in the current environment.
    """
    progress = Signal(str)
    finished = Signal(bool, str)

    def run(self):
        try:
            self.progress.emit("Starting installation of MarkItDown...")
            
            # Using sys.executable ensures it installs in the current python environment
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "markitdown[all]"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output to the UI
            for line in process.stdout:
                self.progress.emit(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.finished.emit(True, "Installation complete. Please restart the app.")
            else:
                self.finished.emit(False, f"Installation failed with return code {process.returncode}")
                
        except Exception as e:
            self.finished.emit(False, f"Installation error: {str(e)}")
