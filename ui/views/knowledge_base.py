"""Knowledge Base browser — Apple-style document list."""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QPushButton, QMessageBox, QListWidgetItem
)
from PySide6.QtCore import Qt, QThreadPool, QUrl
from PySide6.QtGui import QDesktopServices
import subprocess
import os
from ui.theme import AppleColors, AppleTypography
from ui.icons import get_icon
from storage.knowledge_base import KnowledgeBaseManager
from workers.index_worker import IndexWorker


class KnowledgeBaseView(QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(4)
        
        # ── Title ──────────────────────────────────────────────
        title = QLabel("Knowledge Base")
        title.setObjectName("viewTitle")
        layout.addWidget(title)
        
        subtitle = QLabel("Browse, manage, and index your converted documents")
        subtitle.setObjectName("viewSubtitle")
        layout.addWidget(subtitle)
        
        layout.addSpacing(16)
        
        # ── Document Count ─────────────────────────────────────
        self.count_label = QLabel("0 documents")
        self.count_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_TERTIARY};
            font-size: {AppleTypography.SIZE_CALLOUT}px;
        """)
        layout.addWidget(self.count_label)
        
        layout.addSpacing(8)
        
        # ── File List ──────────────────────────────────────────
        self.file_list = QListWidget()
        self.file_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 8px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 5px;
                margin: 1px 2px;
                font-size: {AppleTypography.SIZE_BODY}px;
            }}
            QListWidget::item:selected {{
                background-color: {AppleColors.ACCENT_BLUE};
                color: white;
            }}
        """)
        self.file_list.itemDoubleClicked.connect(self.open_item)
        layout.addWidget(self.file_list)
        
        # ── Action Bar ─────────────────────────────────────────
        layout.addSpacing(8)
        controls = QHBoxLayout()
        controls.setSpacing(8)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_list)
        controls.addWidget(self.btn_refresh)
        
        self.btn_open = QPushButton("Open")
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.clicked.connect(self.open_selected)
        controls.addWidget(self.btn_open)

        self.btn_reveal = QPushButton("Reveal")
        self.btn_reveal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reveal.clicked.connect(self.reveal_selected)
        controls.addWidget(self.btn_reveal)
        
        self.btn_index = QPushButton("Index Selected")
        self.btn_index.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_index.clicked.connect(self.index_selected)
        controls.addWidget(self.btn_index)
        
        controls.addStretch()
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                color: {AppleColors.ACCENT_RED};
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 6px;
                padding: 5px 14px;
            }}
            QPushButton:hover {{
                background-color: #3a2020;
                border-color: {AppleColors.ACCENT_RED};
            }}
        """)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_selected)
        controls.addWidget(self.btn_delete)
        
        layout.addLayout(controls)
        
        self.refresh_list()
        
    def refresh_list(self):
        self.file_list.clear()
        docs = KnowledgeBaseManager.get_all_documents()
        for doc in docs:
            item = QListWidgetItem(f"   {doc.name}")
            item.setIcon(get_icon("document", AppleColors.TEXT_SECONDARY, 16))
            item.setData(Qt.ItemDataRole.UserRole, str(doc))
            self.file_list.addItem(item)
        self.count_label.setText(f"{len(docs)} document{'s' if len(docs) != 1 else ''}")
            
    def index_selected(self):
        items = self.file_list.selectedItems()
        if not items:
            QMessageBox.information(self, "No Selection", "Please select a document to index.")
            return
            
        file_path = items[0].data(Qt.ItemDataRole.UserRole)
        doc_id = Path(file_path).name
        
        worker = IndexWorker(file_path, doc_id)
        worker.signals.finished.connect(
            lambda count: QMessageBox.information(self, "Indexed", f"Successfully indexed {count} chunks.")
        )
        worker.signals.error.connect(
            lambda err: QMessageBox.critical(self, "Error", f"Failed to index:\n{err.split(chr(10))[0]}")
        )
        self.threadpool.start(worker)

    def open_item(self, item):
        file_path = Path(item.data(Qt.ItemDataRole.UserRole))
        if file_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(file_path)))
        else:
            QMessageBox.critical(self, "Error", f"File not found on disk:\n{file_path}")

    def open_selected(self):
        items = self.file_list.selectedItems()
        if not items:
            return
        self.open_item(items[0])

    def reveal_selected(self):
        items = self.file_list.selectedItems()
        if not items:
            return
        file_path = Path(items[0].data(Qt.ItemDataRole.UserRole))
        if file_path.exists():
            if os.name == 'posix':
                subprocess.run(['open', '-R', str(file_path)])
            elif os.name == 'nt':
                subprocess.run(['explorer', '/select,', str(file_path)])
        else:
            QMessageBox.critical(self, "Error", f"File not found on disk:\n{file_path}")
        
    def delete_selected(self):
        items = self.file_list.selectedItems()
        if not items:
            return
            
        file_path = Path(items[0].data(Qt.ItemDataRole.UserRole))
        if KnowledgeBaseManager.delete_document(file_path):
            self.refresh_list()
