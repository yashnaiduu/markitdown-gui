"""
Settings view — Apple System Settings inspired layout with interactive configuration.
Allows configuring Ollama and embedding models, chunk size, and checking connection health.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QFrame, QComboBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from ui.theme import AppleColors, AppleTypography
from core.config import settings
from services.ollama_client import OllamaClient


class SettingsRow(QFrame):
    """A single settings row inside a settings group card."""
    
    def __init__(self, label: str, widget: QWidget, description: str = ""):
        super().__init__()
        self.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(12)
        
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            color: {AppleColors.TEXT_PRIMARY};
            font-size: {AppleTypography.SIZE_BODY}px;
            background: transparent;
        """)
        text_col.addWidget(lbl)
        
        if description:
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setStyleSheet(f"""
                color: {AppleColors.TEXT_TERTIARY};
                font-size: {AppleTypography.SIZE_FOOTNOTE}px;
                background: transparent;
            """)
            text_col.addWidget(desc)
            
        layout.addLayout(text_col)
        layout.addStretch()
        layout.addWidget(widget)


class SettingsGroup(QFrame):
    """A grouped card containing multiple settings rows (like Apple Settings)."""
    
    def __init__(self, title: str):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 10px;
            }}
        """)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 12)
        self._layout.setSpacing(0)
        
        header = QLabel(title.upper())
        header.setStyleSheet(f"""
            color: {AppleColors.TEXT_TERTIARY};
            font-size: {AppleTypography.SIZE_FOOTNOTE}px;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: transparent;
            margin-bottom: 4px;
        """)
        self._layout.addWidget(header)
        
        self._rows_added = 0
        
    def add_row(self, row: SettingsRow):
        if self._rows_added > 0:
            # Add a separator between rows
            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background-color: {AppleColors.SEPARATOR_SUBTLE}; border: none;")
            self._layout.addWidget(sep)
        self._layout.addWidget(row)
        self._rows_added += 1


class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.ollama_client = OllamaClient()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(4)
        
        # ── Title ──────────────────────────────────────────────
        title = QLabel("Settings")
        title.setObjectName("viewTitle")
        layout.addWidget(title)
        
        subtitle = QLabel("Configure application behavior and preferences")
        subtitle.setObjectName("viewSubtitle")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # ── Privacy Group ──────────────────────────────────────
        privacy_group = SettingsGroup("Privacy & Security")
        
        self.chk_offline = QCheckBox()
        self.chk_offline.setChecked(settings.offline_mode)
        self.chk_offline.toggled.connect(self._on_offline_toggled)
        
        privacy_group.add_row(SettingsRow(
            "Strict Offline Mode",
            self.chk_offline,
            "Block all outbound network requests. Only local operations will be available."
        ))
        layout.addWidget(privacy_group)
        
        layout.addSpacing(12)
        
        # ── AI Models Group ────────────────────────────────────
        ai_group = SettingsGroup("AI Models")
        
        # Connection status indicator
        self.lbl_connection = QLabel("● Checking...")
        self.lbl_connection.setStyleSheet(f"color: {AppleColors.TEXT_TERTIARY}; font-size: {AppleTypography.SIZE_BODY}px; background: transparent;")
        ai_group.add_row(SettingsRow(
            "Ollama Daemon Connection",
            self.lbl_connection,
            "Status of your local Ollama daemon (127.0.0.1:11434)."
        ))
        
        # Ollama Model Dropdown
        self.combo_ollama = QComboBox()
        self.combo_ollama.setMinimumWidth(200)
        self.combo_ollama.currentIndexChanged.connect(self._on_ollama_changed)
        ai_group.add_row(SettingsRow(
            "Ollama Model",
            self.combo_ollama,
            "The local LLM used for AI Chat and RAG responses."
        ))
        
        # Embedding Model Dropdown
        self.combo_embed = QComboBox()
        self.combo_embed.setMinimumWidth(200)
        self.combo_embed.addItems([
            "all-MiniLM-L6-v2",
            "all-mpnet-base-v2",
            "paraphrase-multilingual-MiniLM-L12-v2"
        ])
        # Find default
        idx = self.combo_embed.findText(settings.embedding_model)
        if idx >= 0:
            self.combo_embed.setCurrentIndex(idx)
        self.combo_embed.currentIndexChanged.connect(self._on_embed_changed)
        
        ai_group.add_row(SettingsRow(
            "Embedding Model",
            self.combo_embed,
            "Used for generating document embeddings for semantic search."
        ))
        layout.addWidget(ai_group)
        
        layout.addSpacing(12)
        
        # ── RAG Group ──────────────────────────────────────────
        rag_group = SettingsGroup("RAG Pipeline")
        
        self.txt_chunk = QLineEdit()
        self.txt_chunk.setText(str(settings.chunk_size))
        self.txt_chunk.setFixedWidth(80)
        self.txt_chunk.editingFinished.connect(self._on_chunk_changed)
        rag_group.add_row(SettingsRow(
            "Chunk Size",
            self.txt_chunk,
            "Number of characters per chunk when indexing documents."
        ))
        
        self.txt_overlap = QLineEdit()
        self.txt_overlap.setText(str(settings.chunk_overlap))
        self.txt_overlap.setFixedWidth(80)
        self.txt_overlap.editingFinished.connect(self._on_overlap_changed)
        rag_group.add_row(SettingsRow(
            "Chunk Overlap",
            self.txt_overlap,
            "Number of overlapping characters between chunks."
        ))
        layout.addWidget(rag_group)
        
        layout.addStretch()
        
        # Connection status updater timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_connection_status)
        self.status_timer.start(5000) # Every 5s
        
        self._update_connection_status()
        
    def _update_connection_status(self):
        is_connected = self.ollama_client.check_connection()
        if is_connected:
            self.lbl_connection.setText("● Connected")
            self.lbl_connection.setStyleSheet(f"color: {AppleColors.ACCENT_GREEN}; font-weight: bold; background: transparent;")
            
            # Populate models combo box
            current_model = settings.ollama_model
            models = self.ollama_client.list_models()
            
            # Temporarily block signals to avoid triggering handlers while building list
            self.combo_ollama.blockSignals(True)
            self.combo_ollama.clear()
            self.combo_ollama.addItems(models)
            
            idx = self.combo_ollama.findText(current_model)
            if idx >= 0:
                self.combo_ollama.setCurrentIndex(idx)
            elif self.combo_ollama.count() > 0:
                # Fallback to first available model if default not found
                self.combo_ollama.setCurrentIndex(0)
                settings.ollama_model = self.combo_ollama.currentText()
            self.combo_ollama.blockSignals(False)
            
        else:
            self.lbl_connection.setText("● Disconnected")
            self.lbl_connection.setStyleSheet(f"color: {AppleColors.ACCENT_RED}; font-weight: bold; background: transparent;")
            self.combo_ollama.blockSignals(True)
            self.combo_ollama.clear()
            self.combo_ollama.addItem("Start Ollama daemon first")
            self.combo_ollama.blockSignals(False)

    def _on_offline_toggled(self, checked: bool):
        settings.offline_mode = checked
        
    def _on_ollama_changed(self, idx: int):
        model_name = self.combo_ollama.currentText()
        if model_name and model_name != "Start Ollama daemon first":
            settings.ollama_model = model_name
            
    def _on_embed_changed(self, idx: int):
        settings.embedding_model = self.combo_embed.currentText()
        
    def _on_chunk_changed(self):
        try:
            val = int(self.txt_chunk.text().strip())
            if val < 50:
                raise ValueError("Chunk size too small.")
            settings.chunk_size = val
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Chunk size must be an integer greater than 50.")
            self.txt_chunk.setText(str(settings.chunk_size))
            
    def _on_overlap_changed(self):
        try:
            val = int(self.txt_overlap.text().strip())
            if val < 0 or val >= settings.chunk_size:
                raise ValueError("Overlap must be positive and smaller than chunk size.")
            settings.chunk_overlap = val
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Chunk overlap must be between 0 and Chunk Size.")
            self.txt_overlap.setText(str(settings.chunk_overlap))
            
    def refresh(self):
        self._update_connection_status()
