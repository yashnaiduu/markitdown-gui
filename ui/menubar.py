"""
macOS Menu Bar (System Tray) integration with a floating drop zone.
Provides quick drag-and-drop file conversion from the menu bar.
"""

from PySide6.QtWidgets import (
    QSystemTrayIcon, QMenu, QWidget, QVBoxLayout,
    QLabel, QFrame, QApplication
)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PySide6.QtCore import Qt, QSize, QThreadPool, QTimer
from ui.theme import AppleColors, AppleTypography
from ui.icons import get_icon
from workers.convert_worker import ConvertWorker


def _create_tray_icon_pixmap() -> QPixmap:
    """Generate a simple 'M↓' icon for the menu bar."""
    size = 22  # macOS standard menu bar icon size
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw 'M' character
    painter.setPen(QColor("#ffffff"))
    font = QFont(".AppleSystemUIFont", 12)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "M↓")
    
    painter.end()
    return pixmap


class FloatingDropZone(QWidget):
    """
    A small, always-on-top, borderless floating window that accepts drag-and-drop.
    Appears near the menu bar when toggled from the tray icon.
    """
    
    def __init__(self):
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAcceptDrops(True)
        self.setFixedSize(220, 140)
        self.threadpool = QThreadPool()
        
        # ── Layout ─────────────────────────────────────────────
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 220, 140)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {AppleColors.ELEVATED_BG};
                border: 1px solid {AppleColors.SEPARATOR};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_icon("document", AppleColors.TEXT_TERTIARY, 28).pixmap(28, 28))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.icon_label)
        
        self.text_label = QLabel("Drop files here")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_SECONDARY};
            font-size: {AppleTypography.SIZE_BODY}px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(self.text_label)
        
        self.status_label = QLabel("Quick convert to Markdown")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_TERTIARY};
            font-size: {AppleTypography.SIZE_FOOTNOTE}px;
            background: transparent;
        """)
        layout.addWidget(self.status_label)
        
    def _position_near_tray(self):
        """Position the drop zone below the menu bar, right-aligned."""
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.right() - self.width() - 16
            y = geo.top() + 8
            self.move(x, y)
    
    def show(self):
        self._position_near_tray()
        super().show()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.container.setStyleSheet(f"""
                QFrame {{
                    background-color: {AppleColors.ELEVATED_BG};
                    border: 2px solid {AppleColors.ACCENT_BLUE};
                    border-radius: 12px;
                }}
            """)
            self.icon_label.setPixmap(get_icon("arrow_down", AppleColors.ACCENT_BLUE, 28).pixmap(28, 28))
            self.text_label.setText("Release to convert")
            self.text_label.setStyleSheet(f"""
                color: {AppleColors.ACCENT_BLUE};
                font-size: {AppleTypography.SIZE_BODY}px;
                font-weight: 600;
                background: transparent;
            """)

    def dragLeaveEvent(self, event):
        self._reset_style()

    def dropEvent(self, event):
        self._reset_style()
        
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                files.append(file_path)
                
        if files:
            self.icon_label.setPixmap(get_icon("refresh", AppleColors.ACCENT_BLUE, 28).pixmap(28, 28))
            self.text_label.setText(f"Converting {len(files)} file{'s' if len(files) != 1 else ''}...")
            self.status_label.setText("Please wait...")
            
            self._pending = len(files)
            self._successes = 0
            self._errors = 0
            
            # Save mode destination calculation
            from core.config import settings
            dest_mode = settings.output_destination
            dest_dir = None
            if dest_mode == "source":
                from pathlib import Path
                dest_dir = str(Path(files[0]).parent)
            elif dest_mode == "custom":
                dest_dir = settings.custom_output_path
                
            for fp in files:
                worker = ConvertWorker(fp, "file", dest_dir=dest_dir)
                worker.signals.finished.connect(self._on_success)
                worker.signals.error.connect(self._on_error)
                self.threadpool.start(worker)
    
    def _on_success(self, saved_path):
        from core.config import settings
        self._successes += 1
        
        # Trigger index if enabled
        if saved_path and settings.auto_index:
            from workers.index_worker import IndexWorker
            doc_id = saved_path.name
            index_worker = IndexWorker(str(saved_path), doc_id)
            self.threadpool.start(index_worker)
            
        self._check_done()
        
    def _on_error(self, err_msg):
        self._errors += 1
        self._check_done()
        
    def _check_done(self):
        if self._successes + self._errors >= self._pending:
            if self._errors:
                self.icon_label.setPixmap(get_icon("x", AppleColors.ACCENT_RED, 28).pixmap(28, 28))
                self.text_label.setText(f"{self._successes} converted")
                self.status_label.setText(f"{self._errors} failed")
            else:
                self.icon_label.setPixmap(get_icon("check", AppleColors.ACCENT_GREEN, 28).pixmap(28, 28))
                self.text_label.setText(f"{self._successes} converted")
                self.status_label.setText("Saved & Indexed")
                
            # Reset after 3 seconds
            QTimer.singleShot(3000, self._reset_style)
    
    def _reset_style(self):
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {AppleColors.ELEVATED_BG};
                border: 1px solid {AppleColors.SEPARATOR};
                border-radius: 12px;
            }}
        """)
        self.icon_label.setPixmap(get_icon("document", AppleColors.TEXT_TERTIARY, 28).pixmap(28, 28))
        self.text_label.setText("Drop files here")
        self.text_label.setStyleSheet(f"""
            color: {AppleColors.TEXT_SECONDARY};
            font-size: {AppleTypography.SIZE_BODY}px;
            font-weight: 500;
            background: transparent;
        """)
        self.status_label.setText("Quick convert to Markdown")
        
    def mousePressEvent(self, event):
        """Allow dragging the floating window itself."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


class MenuBarManager:
    """Manages the macOS menu bar (system tray) icon and drop zone."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.drop_zone = FloatingDropZone()
        
        # ── Create Tray Icon ───────────────────────────────────
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(_create_tray_icon_pixmap()))
        self.tray_icon.setToolTip("MarkItDown Studio")
        
        # ── Create Menu ────────────────────────────────────────
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {AppleColors.ELEVATED_BG};
                border: 1px solid {AppleColors.SEPARATOR};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 4px;
                color: {AppleColors.TEXT_PRIMARY};
                font-size: {AppleTypography.SIZE_BODY}px;
            }}
            QMenu::item:selected {{
                background-color: {AppleColors.ACCENT_BLUE};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {AppleColors.SEPARATOR_SUBTLE};
                margin: 4px 8px;
            }}
        """)
        
        action_drop = QAction("Quick Convert (Drop Zone)", menu)
        action_drop.setIcon(get_icon("document", AppleColors.TEXT_PRIMARY, 14))
        action_drop.triggered.connect(self.toggle_drop_zone)
        menu.addAction(action_drop)
        
        menu.addSeparator()
        
        action_show = QAction("Show Main Window", menu)
        action_show.setIcon(get_icon("home", AppleColors.TEXT_PRIMARY, 14))
        action_show.triggered.connect(self._show_main_window)
        menu.addAction(action_show)
        
        action_hide = QAction("Hide Main Window", menu)
        action_hide.setIcon(get_icon("x", AppleColors.TEXT_PRIMARY, 14))
        action_hide.triggered.connect(self.main_window.hide)
        menu.addAction(action_hide)
        
        menu.addSeparator()
        
        action_quit = QAction("Quit", menu)
        action_quit.setIcon(get_icon("x", AppleColors.ACCENT_RED, 14))
        action_quit.triggered.connect(QApplication.quit)
        menu.addAction(action_quit)
        
        self.tray_icon.setContextMenu(menu)
        
        # Single click toggles the drop zone
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        self.tray_icon.show()
        
    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Single click
            self.toggle_drop_zone()
    
    def toggle_drop_zone(self):
        if self.drop_zone.isVisible():
            self.drop_zone.hide()
        else:
            self.drop_zone.show()
            
    def _show_main_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
