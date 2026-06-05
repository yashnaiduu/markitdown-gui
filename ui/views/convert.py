"""File conversion view with Apple-style drag & drop zone."""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QProgressBar, QMessageBox, QFrame,
    QListWidgetItem
)
from PySide6.QtCore import Qt, QThreadPool
from ui.theme import AppleColors, AppleTypography
from ui.icons import get_icon
from workers.convert_worker import ConvertWorker
from workers.index_worker import IndexWorker
from ui.components.file_action_widget import FileActionWidget


class DropArea(QFrame):
    """Apple-style drag & drop zone."""
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(140)
        self.files = []
        self._set_idle_style()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_icon("folder", AppleColors.TEXT_TERTIARY, 32).pixmap(32, 32))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.icon_label)
        
        self.text_label = QLabel("Drop files here or click to browse")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_SECONDARY};
            font-size: {AppleTypography.SIZE_BODY}px;
            background: transparent;
        """)
        layout.addWidget(self.text_label)
        
        self.hint_label = QLabel("PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, EPUB, TXT")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_TERTIARY};
            font-size: {AppleTypography.SIZE_FOOTNOTE}px;
            background: transparent;
        """)
        layout.addWidget(self.hint_label)
    
    def _set_idle_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {AppleColors.DROP_BORDER};
                border-radius: 12px;
                background-color: {AppleColors.DROP_BG};
            }}
        """)
        
    def _set_active_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {AppleColors.DROP_BORDER_ACTIVE};
                border-radius: 12px;
                background-color: {AppleColors.DROP_BG_ACTIVE};
            }}
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_active_style()
            self.icon_label.setPixmap(get_icon("folder", AppleColors.ACCENT_BLUE, 32).pixmap(32, 32))

    def dragLeaveEvent(self, event):
        self._set_idle_style()
        self.icon_label.setPixmap(get_icon("folder", AppleColors.TEXT_TERTIARY, 32).pixmap(32, 32))

    def dropEvent(self, event):
        self._set_idle_style()
        self.icon_label.setPixmap(get_icon("folder", AppleColors.TEXT_TERTIARY, 32).pixmap(32, 32))
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path and file_path not in self.files:
                self.files.append(file_path)
        count = len(self.files)
        self.text_label.setText(f"{count} file{'s' if count != 1 else ''} selected")
        self.hint_label.setText("Ready to convert")


class ConvertView(QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(4)
        
        # ── Title ──────────────────────────────────────────────
        title = QLabel("Convert Files")
        title.setObjectName("viewTitle")
        layout.addWidget(title)
        
        subtitle = QLabel("Convert documents to Markdown using MarkItDown")
        subtitle.setObjectName("viewSubtitle")
        layout.addWidget(subtitle)
        
        layout.addSpacing(16)
        
        # ── Drop Zone ──────────────────────────────────────────
        self.drop_area = DropArea()
        layout.addWidget(self.drop_area)
        
        layout.addSpacing(12)
        
        # ── Results List ───────────────────────────────────────
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
                border-radius: 4px;
                margin: 1px 2px;
                font-size: {AppleTypography.SIZE_CALLOUT}px;
            }}
        """)
        layout.addWidget(self.file_list)
        
        # ── Controls ───────────────────────────────────────────
        controls = QHBoxLayout()
        controls.setSpacing(8)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setFixedHeight(6)
        controls.addWidget(self.progress)
        
        controls.addStretch()
        
        self.btn_convert = QPushButton("Convert to Markdown")
        self.btn_convert.setObjectName("primaryButton")
        self.btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_convert.clicked.connect(self.start_conversion)
        controls.addWidget(self.btn_convert)
        
        layout.addSpacing(8)
        layout.addLayout(controls)
        
    def start_conversion(self):
        from core.config import settings
        if not self.drop_area.files:
            QMessageBox.warning(self, "No Files", "Please drop files into the area above first.")
            return
            
        self.btn_convert.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(self.drop_area.files))
        self.progress.setValue(0)
        
        self.completed_count = 0
        self.file_list.clear()
        
        # Calculate destination directory from Settings
        dest_mode = settings.output_destination
        dest_dir = None
        if dest_mode == "source":
            dest_dir = str(Path(self.drop_area.files[0]).parent)
        elif dest_mode == "custom":
            dest_dir = settings.custom_output_path
            
        for file_path in self.drop_area.files:
            worker = ConvertWorker(file_path, "file", dest_dir=dest_dir)
            worker.signals.finished.connect(self.on_convert_finished)
            worker.signals.error.connect(self.on_convert_error)
            self.threadpool.start(worker)
            
    def on_convert_finished(self, saved_path):
        from core.config import settings
        
        # Create custom widget
        item_widget = FileActionWidget(saved_path.name, success=True, file_path=saved_path)
        
        # Add item to list
        item = QListWidgetItem()
        item.setSizeHint(item_widget.sizeHint())
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, item_widget)
        
        # Auto RAG indexing if checked
        if settings.auto_index:
            doc_id = saved_path.name
            index_worker = IndexWorker(str(saved_path), doc_id)
            self.threadpool.start(index_worker)
            
        self._step_progress()
        
    def on_convert_error(self, err_msg):
        # Shorten message
        short_err = err_msg.split("\n")[0]
        
        item_widget = FileActionWidget(short_err, success=False)
        
        item = QListWidgetItem()
        item.setSizeHint(item_widget.sizeHint())
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, item_widget)
        self._step_progress()
        
    def _step_progress(self):
        self.completed_count += 1
        self.progress.setValue(self.completed_count)
        if self.completed_count >= len(self.drop_area.files):
            self.btn_convert.setEnabled(True)
            self.progress.setVisible(False)
            self.drop_area.files.clear()
            self.drop_area.text_label.setText("Drop files here or click to browse")
            self.drop_area.hint_label.setText("PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, EPUB, TXT")
