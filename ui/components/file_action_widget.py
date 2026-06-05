import subprocess
import os
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from ui.theme import AppleColors
from ui.icons import get_icon

class FileActionWidget(QWidget):
    """Custom widget for list items showing file conversion result and actions."""
    def __init__(self, text: str, success: bool = True, file_path: Path = None):
        super().__init__()
        self.file_path = file_path
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Icon
        self.icon_label = QLabel()
        if success:
            self.icon_label.setPixmap(get_icon("check", AppleColors.ACCENT_GREEN, 16).pixmap(16, 16))
        else:
            self.icon_label.setPixmap(get_icon("x", AppleColors.ACCENT_RED, 16).pixmap(16, 16))
        layout.addWidget(self.icon_label)
        
        # Text
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.text_label, 1)  # Stretch factor 1
        
        # Actions (only if success and path provided)
        if success and file_path and file_path.exists():
            self.btn_reveal = QPushButton("Reveal")
            self.btn_reveal.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_reveal.setStyleSheet(self._button_style())
            self.btn_reveal.clicked.connect(self._reveal_file)
            layout.addWidget(self.btn_reveal)
            
            self.btn_open = QPushButton("Open")
            self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_open.setStyleSheet(self._button_style())
            self.btn_open.clicked.connect(self._open_file)
            layout.addWidget(self.btn_open)

    def _button_style(self):
        return f"""
            QPushButton {{
                background-color: {AppleColors.BUTTON_BG};
                border: 1px solid {AppleColors.SEPARATOR};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                min-height: 18px;
            }}
            QPushButton:hover {{
                background-color: {AppleColors.BUTTON_BG_HOVER};
            }}
        """

    def _reveal_file(self):
        if self.file_path:
            if self.file_path.exists():
                try:
                    if os.name == 'posix':
                        subprocess.run(['open', '-R', str(self.file_path)])
                    elif os.name == 'nt':
                        subprocess.run(['explorer', '/select,', str(self.file_path)])
                except Exception as e:
                    QMessageBox.critical(self, "Reveal Failed", str(e))
            else:
                QMessageBox.critical(self, "File Missing", "The file no longer exists on disk.")
                
    def _open_file(self):
        if self.file_path:
            if self.file_path.exists():
                try:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.file_path)))
                except Exception as e:
                    QMessageBox.critical(self, "Open Failed", str(e))
            else:
                QMessageBox.critical(self, "File Missing", "The file no longer exists on disk.")
