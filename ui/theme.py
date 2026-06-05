"""
Apple Human Interface Guidelines inspired theme for MarkItDown Studio.
Design tokens and stylesheet following macOS Sonoma design language.
"""

from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


# ─── Apple Design Tokens ───────────────────────────────────────────────
class AppleColors:
    """macOS Sonoma dark mode color palette."""
    
    # Backgrounds
    WINDOW_BG = "#1e1e1e"
    SIDEBAR_BG = "#252525"
    CONTENT_BG = "#1e1e1e"
    CARD_BG = "#2a2a2a"
    CARD_BG_HOVER = "#303030"
    ELEVATED_BG = "#333333"
    
    # Separators
    SEPARATOR = "#3a3a3a"
    SEPARATOR_SUBTLE = "#2e2e2e"
    
    # Text
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#ababab"
    TEXT_TERTIARY = "#6e6e6e"
    TEXT_QUATERNARY = "#484848"
    
    # Accents (Apple system colors)
    ACCENT_BLUE = "#0A84FF"
    ACCENT_BLUE_HOVER = "#409CFF"
    ACCENT_GREEN = "#30D158"
    ACCENT_RED = "#FF453A"
    ACCENT_ORANGE = "#FF9F0A"
    ACCENT_YELLOW = "#FFD60A"
    ACCENT_PURPLE = "#BF5AF2"
    ACCENT_TEAL = "#64D2FF"
    
    # Interactive
    BUTTON_BG = "#3a3a3a"
    BUTTON_BG_HOVER = "#484848"
    BUTTON_BG_ACTIVE = "#555555"
    BUTTON_PRIMARY_BG = "#0A84FF"
    BUTTON_PRIMARY_HOVER = "#409CFF"
    
    # Sidebar
    SIDEBAR_ITEM_HOVER = "#ffffff0d"       # 5% white
    SIDEBAR_ITEM_SELECTED = "#ffffff14"    # 8% white
    SIDEBAR_SECTION_HEADER = "#6e6e6e"
    
    # Input
    INPUT_BG = "#1a1a1a"
    INPUT_BORDER = "#3a3a3a"
    INPUT_FOCUS_BORDER = "#0A84FF"
    
    # Scrollbar
    SCROLLBAR_BG = "transparent"
    SCROLLBAR_HANDLE = "#ffffff26"          # 15% white
    SCROLLBAR_HANDLE_HOVER = "#ffffff40"    # 25% white
    
    # Drop area
    DROP_BORDER = "#3a3a3a"
    DROP_BORDER_ACTIVE = "#0A84FF"
    DROP_BG = "#1a1a1a"
    DROP_BG_ACTIVE = "#0A84FF0d"


class AppleTypography:
    """SF Pro typography scale following Apple HIG."""
    
    FONT_FAMILY = "SF Pro Text"
    FONT_FAMILY_DISPLAY = "SF Pro Display"
    FONT_FAMILY_MONO = "SF Mono"
    FALLBACK = ".AppleSystemUIFont"
    
    # Sizes (pt)
    SIZE_LARGE_TITLE = 22
    SIZE_TITLE_1 = 20
    SIZE_TITLE_2 = 17
    SIZE_TITLE_3 = 15
    SIZE_HEADLINE = 14
    SIZE_BODY = 13
    SIZE_CALLOUT = 12
    SIZE_SUBHEAD = 11
    SIZE_FOOTNOTE = 10
    SIZE_CAPTION = 9


class ThemeManager:
    """Applies the Apple-native dark theme to the entire application."""
    
    @staticmethod
    def setup_fonts():
        font = QFont(AppleTypography.FONT_FAMILY, AppleTypography.SIZE_BODY)
        if not font.exactMatch():
            font = QFont(AppleTypography.FALLBACK, AppleTypography.SIZE_BODY)
        font.setHintingPreference(QFont.PreferNoHinting)
        QApplication.setFont(font)
        
    @staticmethod
    def apply_dark_theme(app: QApplication):
        app.setStyle("Fusion")
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(AppleColors.WINDOW_BG))
        palette.setColor(QPalette.WindowText, QColor(AppleColors.TEXT_PRIMARY))
        palette.setColor(QPalette.Base, QColor(AppleColors.INPUT_BG))
        palette.setColor(QPalette.AlternateBase, QColor(AppleColors.CARD_BG))
        palette.setColor(QPalette.ToolTipBase, QColor(AppleColors.ELEVATED_BG))
        palette.setColor(QPalette.ToolTipText, QColor(AppleColors.TEXT_PRIMARY))
        palette.setColor(QPalette.Text, QColor(AppleColors.TEXT_PRIMARY))
        palette.setColor(QPalette.Button, QColor(AppleColors.BUTTON_BG))
        palette.setColor(QPalette.ButtonText, QColor(AppleColors.TEXT_PRIMARY))
        palette.setColor(QPalette.Highlight, QColor(AppleColors.ACCENT_BLUE))
        palette.setColor(QPalette.HighlightedText, QColor(AppleColors.TEXT_PRIMARY))
        palette.setColor(QPalette.PlaceholderText, QColor(AppleColors.TEXT_TERTIARY))
        
        app.setPalette(palette)
        app.setStyleSheet(ThemeManager._build_stylesheet())
        
    @staticmethod
    def _build_stylesheet() -> str:
        C = AppleColors
        T = AppleTypography
        
        return f"""
            /* ── Global ─────────────────────────────────────── */
            QMainWindow {{
                background-color: {C.WINDOW_BG};
            }}
            QWidget {{
                color: {C.TEXT_PRIMARY};
                font-family: "{T.FONT_FAMILY}", "{T.FALLBACK}";
                font-size: {T.SIZE_BODY}px;
            }}
            
            /* ── Push Buttons ────────────────────────────────── */
            QPushButton {{
                background-color: {C.BUTTON_BG};
                border: 1px solid {C.SEPARATOR};
                border-radius: 6px;
                padding: 5px 14px;
                font-size: {T.SIZE_BODY}px;
                font-weight: 500;
                min-height: 22px;
            }}
            QPushButton:hover {{
                background-color: {C.BUTTON_BG_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {C.BUTTON_BG_ACTIVE};
            }}
            QPushButton:disabled {{
                color: {C.TEXT_QUATERNARY};
                background-color: {C.CARD_BG};
                border-color: {C.SEPARATOR_SUBTLE};
            }}
            
            /* ── Primary Buttons (use objectName = 'primaryButton') ── */
            QPushButton#primaryButton {{
                background-color: {C.BUTTON_PRIMARY_BG};
                border: none;
                color: white;
                font-weight: 600;
            }}
            QPushButton#primaryButton:hover {{
                background-color: {C.BUTTON_PRIMARY_HOVER};
            }}
            
            /* ── Line Edits ──────────────────────────────────── */
            QLineEdit {{
                background-color: {C.INPUT_BG};
                border: 1px solid {C.INPUT_BORDER};
                border-radius: 6px;
                padding: 5px 10px;
                font-size: {T.SIZE_BODY}px;
                min-height: 22px;
                selection-background-color: {C.ACCENT_BLUE};
            }}
            QLineEdit:focus {{
                border-color: {C.INPUT_FOCUS_BORDER};
            }}
            
            /* ── Text Edits ──────────────────────────────────── */
            QTextEdit, QPlainTextEdit {{
                background-color: {C.INPUT_BG};
                border: 1px solid {C.INPUT_BORDER};
                border-radius: 8px;
                padding: 8px;
                font-size: {T.SIZE_BODY}px;
                selection-background-color: {C.ACCENT_BLUE};
            }}
            QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {C.INPUT_FOCUS_BORDER};
            }}
            
            /* ── List Widgets ────────────────────────────────── */
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 6px 10px;
                border-radius: 5px;
                margin: 1px 6px;
            }}
            QListWidget::item:hover {{
                background-color: {C.SIDEBAR_ITEM_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {C.SIDEBAR_ITEM_SELECTED};
            }}
            
            /* ── Checkboxes ──────────────────────────────────── */
            QCheckBox {{
                spacing: 8px;
                font-size: {T.SIZE_BODY}px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid {C.SEPARATOR};
                background-color: {C.INPUT_BG};
            }}
            QCheckBox::indicator:checked {{
                background-color: {C.ACCENT_BLUE};
                border-color: {C.ACCENT_BLUE};
            }}
            
            /* ── Progress Bars ───────────────────────────────── */
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: {C.SEPARATOR_SUBTLE};
                text-align: center;
                font-size: {T.SIZE_FOOTNOTE}px;
                color: {C.TEXT_SECONDARY};
                max-height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {C.ACCENT_BLUE};
                border-radius: 3px;
            }}
            
            /* ── Scrollbars ──────────────────────────────────── */
            QScrollBar:vertical {{
                border: none;
                background: {C.SCROLLBAR_BG};
                width: 8px;
                margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {C.SCROLLBAR_HANDLE};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {C.SCROLLBAR_HANDLE_HOVER};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {C.SCROLLBAR_BG};
                height: 8px;
                margin: 2px 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {C.SCROLLBAR_HANDLE};
                min-width: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {C.SCROLLBAR_HANDLE_HOVER};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* ── Message Box ─────────────────────────────────── */
            QMessageBox {{
                background-color: {C.ELEVATED_BG};
            }}
            QMessageBox QLabel {{
                color: {C.TEXT_PRIMARY};
            }}
            
            /* ── Tooltips ────────────────────────────────────── */
            QToolTip {{
                background-color: {C.ELEVATED_BG};
                color: {C.TEXT_PRIMARY};
                border: 1px solid {C.SEPARATOR};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: {T.SIZE_FOOTNOTE}px;
            }}
            
            /* ── Combo Box ───────────────────────────────────── */
            QComboBox {{
                background-color: {C.BUTTON_BG};
                border: 1px solid {C.SEPARATOR};
                border-radius: 6px;
                padding: 4px 10px;
                min-height: 22px;
            }}
            QComboBox:hover {{
                background-color: {C.BUTTON_BG_HOVER};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {C.ELEVATED_BG};
                border: 1px solid {C.SEPARATOR};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: {C.ACCENT_BLUE};
            }}
            
            /* ── Form Labels ─────────────────────────────────── */
            QLabel#sectionHeader {{
                color: {C.TEXT_SECONDARY};
                font-size: {T.SIZE_SUBHEAD}px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QLabel#viewTitle {{
                font-family: "{T.FONT_FAMILY_DISPLAY}", "{T.FALLBACK}";
                font-size: {T.SIZE_LARGE_TITLE}px;
                font-weight: 700;
                color: {C.TEXT_PRIMARY};
            }}
            QLabel#viewSubtitle {{
                font-size: {T.SIZE_CALLOUT}px;
                color: {C.TEXT_SECONDARY};
            }}
        """
