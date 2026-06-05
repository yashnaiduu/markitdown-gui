"""
Main application window with Keka-style UI:
1. Compact Mode: A small widget-like interface (300x340) centered on a drag-and-drop zone.
2. Studio Mode: Top toolbar navigation for tools (960x620).
Seamlessly animates window dimensions between modes.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QLabel, QFrame,
    QApplication, QComboBox, QCheckBox, QProgressBar, QPushButton,
    QFileDialog, QToolBar, QToolButton, QMenuBar
)
from PySide6.QtCore import Qt, QSize, QThreadPool, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QScreen, QGuiApplication, QAction, QKeySequence

from core.config import APP_NAME, APP_VERSION, settings
from ui.theme import AppleColors, AppleTypography
from ui.icons import get_icon
from workers.convert_worker import ConvertWorker
from workers.index_worker import IndexWorker

# View imports
from ui.views.dashboard import DashboardView
from ui.views.convert import ConvertView
from ui.views.url_convert import UrlConvertView
from ui.views.knowledge_base import KnowledgeBaseView
from ui.views.chat import ChatView
from ui.views.settings import SettingsView

TOOLBAR_ITEMS = [
    ("home", "Dashboard"),
    ("document", "Convert Files"),
    ("link", "Convert URLs"),
    ("database", "Knowledge Base"),
    ("chat", "AI Chat"),
    ("settings", "Settings"),
]


class CompactDropArea(QFrame):
    """Keka-style compact drag & drop zone."""
    
    def __init__(self, parent: "CompactView"):
        super().__init__(parent)
        self.parent_view: "CompactView" = parent
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_idle_style()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Center Icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_icon("download", AppleColors.TEXT_TERTIARY, 64).pixmap(64, 64))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Instruction Label
        self.lbl_text = QLabel("Drop files here\nor click to browse")
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_text.setStyleSheet(f"""
            color: {AppleColors.TEXT_SECONDARY};
            font-size: {AppleTypography.SIZE_BODY}px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(self.lbl_text)
        
    def _set_idle_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {AppleColors.DROP_BORDER};
                border-radius: 14px;
                background-color: {AppleColors.DROP_BG};
            }}
        """)
        
    def _set_active_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {AppleColors.DROP_BORDER_ACTIVE};
                border-radius: 14px;
                background-color: {AppleColors.DROP_BG_ACTIVE};
            }}
        """)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_active_style()
            self.icon_label.setPixmap(get_icon("download", AppleColors.ACCENT_BLUE, 64).pixmap(64, 64))
            self.lbl_text.setText("Release to Convert")
            self.lbl_text.setStyleSheet(f"color: {AppleColors.ACCENT_BLUE}; font-weight: 600; background: transparent;")
            
    def dragLeaveEvent(self, event):
        self._set_idle_style()
        self.icon_label.setPixmap(get_icon("download", AppleColors.TEXT_TERTIARY, 64).pixmap(64, 64))
        self.lbl_text.setText("Drop files here\nor click to browse")
        self.lbl_text.setStyleSheet(f"color: {AppleColors.TEXT_SECONDARY}; font-weight: 500; background: transparent;")
        
    def dropEvent(self, event):
        self._set_idle_style()
        self.icon_label.setPixmap(get_icon("download", AppleColors.TEXT_TERTIARY, 64).pixmap(64, 64))
        self.lbl_text.setText("Drop files here\nor click to browse")
        self.lbl_text.setStyleSheet(f"color: {AppleColors.TEXT_SECONDARY}; font-weight: 500; background: transparent;")
        
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                files.append(file_path)
                
        if files:
            self.parent_view.start_file_conversion(files)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Open file dialog
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "Select Files to Convert", "",
                "All Supported (*.pdf *.docx *.pptx *.xlsx *.html *.csv *.json *.epub *.txt);;All Files (*)"
            )
            if file_paths:
                self.parent_view.start_file_conversion(file_paths)


class CompactView(QWidget):
    """The compact widget interface centered around the drop area."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.threadpool = QThreadPool()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)
        
        # ── Top bar: Settings row ──────────────────────────────
        top_layout = QHBoxLayout()
        top_layout.setSpacing(6)
        
        self.combo_dest = QComboBox()
        self.combo_dest.addItem(get_icon("database", AppleColors.TEXT_SECONDARY, 14), "To Knowledge Base", "kb")
        self.combo_dest.addItem(get_icon("folder", AppleColors.TEXT_SECONDARY, 14), "Next to original files", "source")
        self.combo_dest.addItem(get_icon("external_link", AppleColors.TEXT_SECONDARY, 14), "To Custom folder...", "custom")
        
        # Select default from config
        idx = self.combo_dest.findData(settings.output_destination)
        if idx >= 0:
            self.combo_dest.setCurrentIndex(idx)
        self.combo_dest.currentIndexChanged.connect(self._on_dest_changed)
        
        top_layout.addWidget(self.combo_dest, 1)
        
        # Icon-only mini toggles
        self.chk_index = QCheckBox("Index")
        self.chk_index.setToolTip("Auto-index converted document to vector store for AI Chat.")
        self.chk_index.setChecked(settings.auto_index)
        self.chk_index.toggled.connect(self._on_index_toggled)
        top_layout.addWidget(self.chk_index)
        
        layout.addLayout(top_layout)
        
        # ── Drop Area ──────────────────────────────────────────
        self.drop_area = CompactDropArea(self)
        layout.addWidget(self.drop_area, 1)
        
        # ── Progress and status ────────────────────────────────
        progress_layout = QHBoxLayout()
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet(f"color: {AppleColors.TEXT_TERTIARY}; font-size: {AppleTypography.SIZE_FOOTNOTE}px;")
        progress_layout.addWidget(self.lbl_status)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        progress_layout.addWidget(self.progress)
        layout.addLayout(progress_layout)
        
        # ── Expand Button ──────────────────────────────────────
        self.btn_expand = QPushButton("Show Studio")
        self.btn_expand.setIcon(get_icon("chevron_right", "#ffffff", 14))
        self.btn_expand.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppleColors.CARD_BG};
                border: 1px solid {AppleColors.SEPARATOR_SUBTLE};
                border-radius: 8px;
                padding: 6px;
                font-weight: 500;
                font-size: {AppleTypography.SIZE_CALLOUT}px;
            }}
            QPushButton:hover {{
                background-color: {AppleColors.CARD_BG_HOVER};
            }}
        """)
        self.btn_expand.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_expand.clicked.connect(self.main_window.expand_to_studio)
        layout.addWidget(self.btn_expand)
        
    def _on_dest_changed(self, idx: int):
        data = self.combo_dest.itemData(idx)
        if data == "custom":
            custom_dir = QFileDialog.getExistingDirectory(self, "Select Custom Output Directory", settings.custom_output_path)
            if custom_dir:
                settings.custom_output_path = custom_dir
                settings.output_destination = "custom"
                # Update item tooltip/text temporarily
                self.combo_dest.setItemText(idx, f"To: {{Path(custom_dir).name}}")
            else:
                # Revert selection to KB
                self.combo_dest.setCurrentIndex(0)
                settings.output_destination = "kb"
        else:
            settings.output_destination = data
            
    def _on_index_toggled(self, checked: bool):
        settings.auto_index = checked
        
    def start_file_conversion(self, file_paths: list[str]):
        if not file_paths:
            return
            
        self.combo_dest.setEnabled(False)
        self.chk_index.setEnabled(False)
        self.btn_expand.setEnabled(False)
        
        self.progress.setVisible(True)
        self.progress.setMaximum(len(file_paths))
        self.progress.setValue(0)
        
        self.completed_count = 0
        self.success_count = 0
        self.error_count = 0
        
        self.total_files = len(file_paths)
        self.lbl_status.setText(f"Converting 1/{{self.total_files}}...")
        
        # Save mode destination calculation
        dest_mode = settings.output_destination
        dest_dir = None
        if dest_mode == "source":
            dest_dir = str(Path(file_paths[0]).parent)
        elif dest_mode == "custom":
            dest_dir = settings.custom_output_path
            
        for fp in file_paths:
            worker = ConvertWorker(fp, "file", dest_dir=dest_dir)
            worker.signals.finished.connect(self.on_convert_finished)
            worker.signals.error.connect(self.on_convert_error)
            self.threadpool.start(worker)
            
    def on_convert_finished(self, saved_path):
        self.success_count += 1
        self._step_progress(saved_path)
        
    def on_convert_error(self, err_msg):
        self.error_count += 1
        self._step_progress(None)
        
    def _step_progress(self, saved_path):
        self.completed_count += 1
        self.progress.setValue(self.completed_count)
        
        # Trigger index if enabled
        if saved_path and settings.auto_index:
            doc_id = saved_path.name
            index_worker = IndexWorker(str(saved_path), doc_id)
            self.threadpool.start(index_worker)
            
        if self.completed_count >= self.total_files:
            # All done
            self.combo_dest.setEnabled(True)
            self.chk_index.setEnabled(True)
            self.btn_expand.setEnabled(True)
            self.progress.setVisible(False)
            
            status_text = f"Converted {{self.success_count}} file{{'s' if self.success_count != 1 else ''}}"
            if self.error_count > 0:
                status_text += f" ({{self.error_count}} failed)"
            self.lbl_status.setText(status_text)
            
            # Reset text after 3.5 seconds
            from PySide6.QtCore import QTimer as _QTimer
            _QTimer.singleShot(3500, lambda: self.lbl_status.setText("Ready"))
        else:
            self.lbl_status.setText(f"Converting {{self.completed_count + 1}}/{{self.total_files}}...")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        
        # Track active transitions
        self.is_expanded = False
        
        # ── Central Widget (Stacked Views) ──────────────────────
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.main_stack = QStackedWidget()
        main_layout.addWidget(self.main_stack)
        
        # Build views
        self.compact_view = CompactView(self)
        self.main_stack.addWidget(self.compact_view)
        
        self._setup_studio_widget()
        self.main_stack.addWidget(self.studio_widget)
        
        # Unified title look
        self.setUnifiedTitleAndToolBarOnMac(True)
        
        # Start in compact mode
        self.collapse_to_drop_zone()
        
        self._setup_menus()
        
    def _setup_studio_widget(self):
        """Construct the full studio mode dashboard container with Toolbar."""
        self.studio_widget = QWidget()
        layout = QVBoxLayout(self.studio_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._setup_toolbar()
        self._setup_content_area()
        
        layout.addWidget(self.toolbar_container)
        layout.addWidget(self.content_area)
        
    def _setup_toolbar(self):
        """Build the Apple-style top toolbar."""
        self.toolbar_container = QFrame()
        self.toolbar_container.setFixedHeight(60)
        self.toolbar_container.setStyleSheet(f"""
            QFrame {{
                background-color: {AppleColors.SIDEBAR_BG};
                border-bottom: 1px solid {AppleColors.SEPARATOR_SUBTLE};
            }}
        """)
        
        toolbar_layout = QHBoxLayout(self.toolbar_container)
        toolbar_layout.setContentsMargins(16, 0, 16, 0)
        toolbar_layout.setSpacing(12)
        
        # ── Collapse Button ────────────────────────────────────
        self.btn_collapse = QPushButton()
        self.btn_collapse.setIcon(get_icon("chevron_left", "#ffffff", 18))
        self.btn_collapse.setToolTip("Collapse to Drop Zone")
        self.btn_collapse.setFixedSize(36, 36)
        self.btn_collapse.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {AppleColors.SIDEBAR_ITEM_HOVER};
            }}
        """)
        self.btn_collapse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_collapse.clicked.connect(self.collapse_to_drop_zone)
        toolbar_layout.addWidget(self.btn_collapse)
        
        # ── Separator ──────────────────────────────────────────
        v_sep = QFrame()
        v_sep.setFrameShape(QFrame.Shape.VLine)
        v_sep.setStyleSheet(f"background-color: {AppleColors.SEPARATOR_SUBTLE}; width: 1px; border: none; margin: 12px 0px;")
        toolbar_layout.addWidget(v_sep)
        
        # ── Navigation Buttons ─────────────────────────────────
        self.nav_buttons = []
        for i, (icon_name, label) in enumerate(TOOLBAR_ITEMS):
            btn = QToolButton()
            btn.setText(label)
            btn.setIcon(get_icon(icon_name, AppleColors.TEXT_SECONDARY, 20))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    padding: 4px 10px;
                    color: {AppleColors.TEXT_SECONDARY};
                    font-size: 10px;
                }}
                QToolButton:hover {{
                    background-color: {AppleColors.SIDEBAR_ITEM_HOVER};
                    color: {AppleColors.TEXT_PRIMARY};
                }}
                QToolButton:checked {{
                    background-color: {AppleColors.SIDEBAR_ITEM_SELECTED};
                    color: {AppleColors.TEXT_PRIMARY};
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self._on_toolbar_clicked(idx))
            self.nav_buttons.append(btn)
            toolbar_layout.addWidget(btn)
            
        # Select first item by default
        self.nav_buttons[0].setChecked(True)
        
        toolbar_layout.addStretch()
        
    def _setup_content_area(self):
        """Set up the stacked content area below the toolbar."""
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {AppleColors.CONTENT_BG};
            }}
        """)
        
        # Add views in the same order as TOOLBAR_ITEMS
        self.content_area.addWidget(DashboardView())
        self.content_area.addWidget(ConvertView())
        self.content_area.addWidget(UrlConvertView())
        self.content_area.addWidget(KnowledgeBaseView())
        self.content_area.addWidget(ChatView())
        self.content_area.addWidget(SettingsView())
        
    def _on_toolbar_clicked(self, index: int):
        if 0 <= index < self.content_area.count():
            self.content_area.setCurrentIndex(index)
            # Refresh lists or statistics on navigate
            view = self.content_area.widget(index)
            if hasattr(view, "refresh"):
                view.refresh()
            elif hasattr(view, "refresh_list"):
                view.refresh_list()
                
            # Update icons (selected vs unselected)
            for i, btn in enumerate(self.nav_buttons):
                icon_name = TOOLBAR_ITEMS[i][0]
                color = AppleColors.TEXT_PRIMARY if i == index else AppleColors.TEXT_SECONDARY
                btn.setIcon(get_icon(icon_name, color, 20))

    def expand_to_studio(self):
        self.animate_window_transition(800, 600, show_studio=True)
        
    def collapse_to_drop_zone(self):
        self.animate_window_transition(300, 340, show_studio=False)
        
    def animate_window_transition(self, target_w: int, target_h: int, show_studio: bool):
        """Keka-style window scaling transition with interpolation."""
        self.is_expanded = show_studio
        
        # Switch main stack configuration
        if show_studio:
            # Enforce layout flexibility
            self.setMinimumSize(700, 450)
            self.setMaximumSize(16777215, 16777215)
            self.main_stack.setCurrentIndex(1)
        else:
            # Enforce fixed small shape
            self.setMinimumSize(target_w, target_h)
            self.setMaximumSize(target_w, target_h)
            self.main_stack.setCurrentIndex(0)
            
        screen = QGuiApplication.primaryScreen()
        if not screen:
            self.resize(target_w, target_h)
            return
            
        start_rect = self.geometry()
        
        # Maintain window center point
        center = start_rect.center()
        target_x = center.x() - target_w // 2
        target_y = center.y() - target_h // 2
        
        target_rect = QRect(target_x, target_y, target_w, target_h)
        
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(350)
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(target_rect)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    def _setup_menus(self):
        """Set up the standard macOS menu bar and global shortcuts."""
        # A parentless QMenuBar on macOS acts as the global system menu bar
        self._global_menubar = QMenuBar()
        menubar = self._global_menubar
        
        # ── Application Menu (MarkItDown Studio) ────────────────
        # Qt automatically builds the App menu from actions with specific roles
        app_menu = menubar.addMenu("MarkItDown Studio")
        
        about_action = QAction("About MarkItDown Studio", self)
        about_action.setMenuRole(QAction.MenuRole.AboutRole)
        app_menu.addAction(about_action)
        
        prefs_action = QAction("Preferences...", self)
        prefs_action.setShortcut(QKeySequence("Ctrl+,")) # Cmd+,
        prefs_action.setMenuRole(QAction.MenuRole.PreferencesRole)
        app_menu.addAction(prefs_action)
        
        hide_action = QAction("Hide MarkItDown Studio", self)
        hide_action.setShortcut(QKeySequence("Ctrl+H")) # Cmd+H
        hide_action.triggered.connect(self.hide)
        app_menu.addAction(hide_action)
        
        quit_action = QAction("Quit MarkItDown Studio", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q")) # Cmd+Q
        quit_action.setMenuRole(QAction.MenuRole.QuitRole)
        quit_action.triggered.connect(QApplication.quit)
        app_menu.addAction(quit_action)
        
        # ── File Menu ───────────────────────────────────────────
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Session", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(lambda: self.content_area.setCurrentIndex(0))
        file_menu.addAction(new_action)
        
        open_action = QAction("Open File...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("Close Window", self)
        close_action.setShortcut(QKeySequence("Ctrl+W")) # Cmd+W
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)
        
        # ── Edit Menu ───────────────────────────────────────────
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence("Ctrl+X"))
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        edit_menu.addAction(paste_action)
        
        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        edit_menu.addAction(select_all_action)
        
        # ── Window Menu ─────────────────────────────────────────
        window_menu = menubar.addMenu("Window")
        
        minimize_action = QAction("Minimize", self)
        minimize_action.setShortcut(QKeySequence("Ctrl+M")) # Cmd+M
        minimize_action.triggered.connect(self.showMinimized)
        window_menu.addAction(minimize_action)
        
        zoom_action = QAction("Zoom", self)
        zoom_action.triggered.connect(self.showMaximized)
        window_menu.addAction(zoom_action)
        
        window_menu.addSeparator()
        
        show_action = QAction("Show Main Window", self)
        show_action.triggered.connect(lambda: (self.show(), self.raise_(), self.activateWindow()))
        window_menu.addAction(show_action)
