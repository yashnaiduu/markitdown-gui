"""Dashboard view — Apple-style stat cards and quick actions."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from ui.theme import AppleColors, AppleTypography
from core.config import settings
from storage.knowledge_base import KnowledgeBaseManager
from ui.icons import get_icon


class StatCard(QFrame):
    """A single statistics card in the Apple dashboard style."""
    
    def __init__(self, icon_name: str, title: str, value: str, accent: str = AppleColors.ACCENT_BLUE):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppleColors.CARD_BG};
                border-radius: 10px;
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
            }}
            QFrame:hover {{
                background-color: {AppleColors.CARD_BG_HOVER};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)
        
        # Icon + Title row
        header = QHBoxLayout()
        header.setSpacing(8)
        
        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon_name, accent, 18).pixmap(18, 18))
        icon_label.setStyleSheet("background: transparent;")
        header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_SECONDARY};
            font-size: {AppleTypography.SIZE_CALLOUT}px;
            font-weight: 500;
            background: transparent;
        """)
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_PRIMARY};
            font-family: "{AppleTypography.FONT_FAMILY_DISPLAY}", "{AppleTypography.FALLBACK}";
            font-size: {AppleTypography.SIZE_TITLE_1}px;
            font-weight: 700;
            background: transparent;
        """)
        layout.addWidget(self.value_label)


class QuickActionButton(QPushButton):
    """An Apple-style quick action button."""
    
    def __init__(self, icon_name: str, label: str):
        super().__init__(f"   {label}")
        self.setIcon(get_icon(icon_name, AppleColors.TEXT_PRIMARY, 16))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 8px;
                padding: 10px 16px;
                font-size: {AppleTypography.SIZE_BODY}px;
                text-align: left;
                color: {AppleColors.TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {AppleColors.CARD_BG_HOVER};
                border-color: {AppleColors.SEPARATOR};
            }}
            QPushButton:pressed {{
                background-color: {AppleColors.BUTTON_BG_ACTIVE};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(4)
        
        # ── Title ──────────────────────────────────────────────
        title = QLabel("Dashboard")
        title.setObjectName("viewTitle")
        layout.addWidget(title)
        
        subtitle = QLabel("Overview of your local knowledge base")
        subtitle.setObjectName("viewSubtitle")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # ── Stat Cards Grid ────────────────────────────────────
        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        layout.addLayout(self.grid)
        
        layout.addSpacing(20)
        
        # ── Quick Actions ──────────────────────────────────────
        actions_header = QLabel("QUICK ACTIONS")
        actions_header.setObjectName("sectionHeader")
        layout.addWidget(actions_header)
        
        layout.addSpacing(8)
        
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        actions_row.addWidget(QuickActionButton("document", "Convert File"))
        actions_row.addWidget(QuickActionButton("link", "Paste URL"))
        actions_row.addWidget(QuickActionButton("play", "YouTube"))
        actions_row.addWidget(QuickActionButton("database", "Knowledge Base"))
        layout.addLayout(actions_row)
        
        layout.addStretch()
        
        self.refresh()
        
    def refresh(self):
        # Clear existing cards
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)
            
        docs = KnowledgeBaseManager.get_all_documents()
        
        cards = [
            ("document", "Documents", str(len(docs)), AppleColors.ACCENT_BLUE),
            ("sparkles", "AI Model", settings.ollama_model, AppleColors.ACCENT_PURPLE),
            ("database", "Embeddings", settings.embedding_model.split("/")[-1], AppleColors.ACCENT_TEAL),
            ("lock", "Privacy", "Local Only" if settings.offline_mode else "Cloud OK", AppleColors.ACCENT_GREEN),
        ]
        
        for i, (icon_name, title, value, accent) in enumerate(cards):
            row, col = divmod(i, 2)
            self.grid.addWidget(StatCard(icon_name, title, value, accent), row, col)
