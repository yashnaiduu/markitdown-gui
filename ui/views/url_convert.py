"""URL & YouTube conversion view — Apple-style input card."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QFrame, QListWidgetItem
)
from PySide6.QtCore import Qt, QThreadPool
from ui.theme import AppleColors, AppleTypography
from ui.icons import get_icon
from workers.convert_worker import ConvertWorker
from ui.components.file_action_widget import FileActionWidget


class UrlConvertView(QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(4)
        
        # ── Title ──────────────────────────────────────────────
        title = QLabel("Convert URLs")
        title.setObjectName("viewTitle")
        layout.addWidget(title)
        
        subtitle = QLabel("Fetch and convert web pages or YouTube videos to Markdown")
        subtitle.setObjectName("viewSubtitle")
        layout.addWidget(subtitle)
        
        layout.addSpacing(16)
        
        # ── Input Card ─────────────────────────────────────────
        input_card = QFrame()
        input_card.setStyleSheet(f"""
            QFrame {{
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 10px;
            }}
        """)
        card_layout = QVBoxLayout(input_card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(10)
        
        card_label = QLabel("Enter a URL")
        card_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_SECONDARY};
            font-size: {AppleTypography.SIZE_CALLOUT}px;
            font-weight: 500;
            background: transparent;
        """)
        card_layout.addWidget(card_label)
        
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://example.com or YouTube link...")
        self.input_url.returnPressed.connect(self.start_conversion)
        input_row.addWidget(self.input_url)
        
        self.btn_convert = QPushButton("Convert")
        self.btn_convert.setObjectName("primaryButton")
        self.btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_convert.clicked.connect(self.start_conversion)
        input_row.addWidget(self.btn_convert)
        
        card_layout.addLayout(input_row)
        layout.addWidget(input_card)
        
        layout.addSpacing(12)
        
        # ── Results Header ─────────────────────────────────────
        results_header = QLabel("RESULTS")
        results_header.setObjectName("sectionHeader")
        layout.addWidget(results_header)
        
        layout.addSpacing(4)
        
        # ── Results List ───────────────────────────────────────
        self.result_list = QListWidget()
        self.result_list.setStyleSheet(f"""
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
        layout.addWidget(self.result_list)
        
    def start_conversion(self):
        url = self.input_url.text().strip()
        if not url:
            return
            
        source_type = "youtube" if ("youtube.com" in url or "youtu.be" in url) else "url"
        
        self.btn_convert.setEnabled(False)
        
        # Pending item
        self.active_item_widget = FileActionWidget(f"Converting {url}...", success=True)
        self.active_item_widget.icon_label.setPixmap(get_icon("refresh", AppleColors.TEXT_TERTIARY, 16).pixmap(16, 16))
        
        item = QListWidgetItem()
        item.setSizeHint(self.active_item_widget.sizeHint())
        self.result_list.addItem(item)
        self.result_list.setItemWidget(item, self.active_item_widget)
        
        # Store index to update later
        self.active_item = item
        
        worker = ConvertWorker(url, source_type)
        worker.signals.finished.connect(self.on_convert_finished)
        worker.signals.error.connect(self.on_convert_error)
        self.threadpool.start(worker)
        
    def on_convert_finished(self, saved_path):
        new_widget = FileActionWidget(saved_path.name, success=True, file_path=saved_path)
        self.active_item.setSizeHint(new_widget.sizeHint())
        self.result_list.setItemWidget(self.active_item, new_widget)
        
        self.btn_convert.setEnabled(True)
        self.input_url.clear()
        
    def on_convert_error(self, err_msg):
        short_err = err_msg.split("\n")[0]
        
        new_widget = FileActionWidget(short_err, success=False)
        self.active_item.setSizeHint(new_widget.sizeHint())
        self.result_list.setItemWidget(self.active_item, new_widget)
        
        self.btn_convert.setEnabled(True)
