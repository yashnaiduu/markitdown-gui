from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from ui.theme import AppleColors, AppleTypography

class PreviewDialog(QDialog):
    """An Apple-style dialog for previewing rendered Markdown."""
    
    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(f"Preview - {file_path.name}")
        self.resize(800, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {AppleColors.BACKGROUND_PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Browser
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {AppleColors.CARD_BG};
                color: {AppleColors.TEXT_PRIMARY};
                font-size: {AppleTypography.SIZE_BODY}px;
                border: none;
                padding: 24px;
            }}
        """)
        layout.addWidget(self.browser)
        
        # Footer
        footer = QHBoxLayout()
        footer.setContentsMargins(16, 12, 16, 12)
        
        footer.addStretch()
        
        btn_close = QPushButton("Close")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppleColors.BUTTON_BG};
                border: 1px solid {AppleColors.SEPARATOR};
                border-radius: 6px;
                padding: 6px 16px;
                font-size: {AppleTypography.SIZE_BODY}px;
                color: {AppleColors.TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {AppleColors.BUTTON_BG_HOVER};
            }}
        """)
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        
        layout.addLayout(footer)
        
        self._load_content()
        
    def _load_content(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            self.browser.setMarkdown(content)
        except Exception as e:
            self.browser.setPlainText(f"Error loading preview: {e}")
