import sys
from PySide6.QtWidgets import QApplication
from core.config import settings, APP_NAME, APP_VERSION
from storage.knowledge_base import KnowledgeBaseManager
from ui.app import MainWindow
from ui.theme import ThemeManager
from ui.menubar import MenuBarManager

def main():
    # Setup knowledge base directories
    KnowledgeBaseManager.setup_directories()
    
    app = QApplication(sys.argv)
    
    # Prevent app from quitting when main window is closed (keep tray alive)
    app.setQuitOnLastWindowClosed(False)
    
    ThemeManager.setup_fonts()
    ThemeManager.apply_dark_theme(app)
    
    print(f"[{APP_NAME}] Starting... Offline mode is: {'Enabled' if settings.offline_mode else 'Disabled'}")
    
    window = MainWindow()
    window.show()
    
    # Setup menu bar icon & floating drop zone
    menubar = MenuBarManager(window)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
