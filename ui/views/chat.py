"""AI Chat view — Apple Messages-inspired chat interface."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QCheckBox, QLineEdit, QLabel, QFrame, QComboBox
)
from PySide6.QtCore import Qt, QThreadPool
from ui.theme import AppleColors, AppleTypography
from ui.icons import get_icon
from workers.chat_worker import ChatWorker
from services.ollama_client import OllamaClient


class ChatView(QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.ollama_client = OllamaClient()
        self.history = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 16)
        layout.setSpacing(4)
        
        # ── Header Bar ─────────────────────────────────────────
        header_layout = QHBoxLayout()
        
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("AI Chat")
        title.setObjectName("viewTitle")
        title_col.addWidget(title)
        
        self.lbl_subtitle = QLabel("Chat with your local Ollama model — optionally powered by RAG")
        self.lbl_subtitle.setObjectName("viewSubtitle")
        title_col.addWidget(self.lbl_subtitle)
        
        header_layout.addLayout(title_col)
        header_layout.addStretch()
        
        # Model Selector Combo box
        self.combo_model = QComboBox()
        self.combo_model.setMinimumWidth(150)
        self.combo_model.currentIndexChanged.connect(self._on_model_changed)
        header_layout.addWidget(self.combo_model)
        
        # Clear Chat Button
        self.btn_clear = QPushButton()
        self.btn_clear.setIcon(get_icon("trash", AppleColors.TEXT_PRIMARY, 14))
        self.btn_clear.setToolTip("Clear conversational history")
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 6px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {AppleColors.CARD_BG_HOVER};
            }}
        """)
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_chat)
        header_layout.addWidget(self.btn_clear)
        
        layout.addLayout(header_layout)
        layout.addSpacing(12)
        
        # ── Chat Display ───────────────────────────────────────
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 10px;
                padding: 12px;
                font-size: {AppleTypography.SIZE_BODY}px;
                line-height: 1.5;
            }}
        """)
        layout.addWidget(self.chat_display)
        
        layout.addSpacing(8)
        
        # ── Input Bar ──────────────────────────────────────────
        input_container = QFrame()
        input_container.setStyleSheet(f"""
            QFrame {{
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 10px;
            }}
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(12, 8, 8, 8)
        input_layout.setSpacing(8)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message Ollama...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                font-size: {AppleTypography.SIZE_BODY}px;
                padding: 4px 0px;
            }}
        """)
        input_layout.addWidget(self.input_field)
        
        self.chk_rag = QCheckBox("RAG")
        self.chk_rag.setToolTip("Search your knowledge base for context")
        self.chk_rag.setStyleSheet(f"""
            QCheckBox {{
                color: {AppleColors.TEXT_TERTIARY};
                font-size: {AppleTypography.SIZE_CALLOUT}px;
            }}
        """)
        input_layout.addWidget(self.chk_rag)
        
        self.btn_send = QPushButton()
        self.btn_send.setIcon(get_icon("arrow_up", "#ffffff", 14))
        self.btn_send.setFixedSize(30, 30)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppleColors.ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 15px;
            }}
            QPushButton:hover {{
                background-color: {AppleColors.ACCENT_BLUE_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {AppleColors.TEXT_QUATERNARY};
            }}
        """)
        self.btn_send.clicked.connect(self.send_message)
        input_layout.addWidget(self.btn_send)
        
        layout.addWidget(input_container)
        
        self.refresh()
        
    def refresh(self):
        """Dynamic connection and model checks."""
        is_connected = self.ollama_client.check_connection()
        if is_connected:
            self.input_field.setEnabled(True)
            self.btn_send.setEnabled(True)
            self.lbl_subtitle.setText("Chat with your local Ollama model — optionally powered by RAG")
            self.lbl_subtitle.setStyleSheet(f"color: {AppleColors.TEXT_SECONDARY};")
            
            from core.config import settings
            current_model = settings.ollama_model
            models = self.ollama_client.list_models()
            
            self.combo_model.blockSignals(True)
            self.combo_model.clear()
            self.combo_model.addItems(models)
            idx = self.combo_model.findText(current_model)
            if idx >= 0:
                self.combo_model.setCurrentIndex(idx)
            self.combo_model.blockSignals(False)
        else:
            self.input_field.setEnabled(False)
            self.input_field.setPlaceholderText("Ollama Disconnected (Start Ollama to Chat)")
            self.btn_send.setEnabled(False)
            self.lbl_subtitle.setText("Local Ollama daemon is offline. Run `ollama serve` to connect.")
            self.lbl_subtitle.setStyleSheet(f"color: {AppleColors.ACCENT_RED};")
            
            self.combo_model.blockSignals(True)
            self.combo_model.clear()
            self.combo_model.addItem("Disconnected")
            self.combo_model.blockSignals(False)
            
    def _on_model_changed(self, idx: int):
        from core.config import settings
        model_name = self.combo_model.currentText()
        if model_name and model_name != "Disconnected":
            settings.ollama_model = model_name
            
    def clear_chat(self):
        self.history.clear()
        self.chat_display.clear()
        self.chat_display.append(
            f'<div style="color: {AppleColors.TEXT_TERTIARY}; text-align: center; '
            f'margin-top: 10px;">Chat history cleared</div>'
        )
        
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.btn_send.setEnabled(False)
        
        # Display user message
        self.chat_display.append(
            f'<div style="color: {AppleColors.ACCENT_BLUE}; font-weight: 600; '
            f'margin-top: 8px;">You</div>'
        )
        self.chat_display.append(f'<div style="margin-bottom: 12px;">{text}</div>')
        
        # Display assistant header
        model_name = self.combo_model.currentText()
        self.chat_display.append(
            f'<div style="color: {AppleColors.ACCENT_PURPLE}; font-weight: 600; '
            f'margin-top: 8px;">{model_name}</div>'
        )
        
        worker = ChatWorker(
            prompt=text,
            history=self.history.copy(),
            use_rag=self.chk_rag.isChecked()
        )
        worker.signals.chunk_received.connect(self.on_chunk)
        worker.signals.finished.connect(self.on_finished)
        worker.signals.error.connect(self.on_error)
        
        self.threadpool.start(worker)
        
    def on_chunk(self, chunk: str):
        self.chat_display.insertPlainText(chunk)
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def on_finished(self):
        self.chat_display.append('<div style="margin-bottom: 12px;"></div>')
        self.input_field.setEnabled(True)
        self.btn_send.setEnabled(True)
        self.input_field.setFocus()
        
    def on_error(self, err: str):
        self.chat_display.append(
            f'<div style="color: {AppleColors.ACCENT_RED}; margin-bottom: 12px;">'
            f'Error: {err.split(chr(10))[0]}</div>'
        )
        self.input_field.setEnabled(True)
        self.btn_send.setEnabled(True)
