import datetime
import json
import os
from pathlib import Path
from PySide6.QtCore import QObject, Signal

from core.config import settings, KB_LOGS_DIR

class ConnectionLogger:
    def __init__(self):
        self.log_file = KB_LOGS_DIR / "network.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def log(self, host: str, action: str):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "time": now,
            "host": host,
            "action": action
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
    def get_logs(self):
        if not self.log_file.exists():
            return []
        logs = []
        with open(self.log_file, "r") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line.strip()))
        return logs

    def clear_logs(self):
        if self.log_file.exists():
            self.log_file.unlink()


class NetworkGuardSignals(QObject):
    connection_detected = Signal(str, str) # host, status


class NetworkGuard:
    """
    Enforces privacy settings. All network requests must be validated here.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkGuard, cls).__new__(cls)
            cls._instance._init_guard()
        return cls._instance
        
    def _init_guard(self):
        self.logger = ConnectionLogger()
        self.signals = NetworkGuardSignals()
        
    def check(self, host: str, require_user_intent: bool = False) -> bool:
        """
        Check if a network connection to `host` is allowed.
        `require_user_intent` should be True if this is an explicit user action (e.g. converting a URL).
        """
        if settings.offline_mode:
            self._log_and_emit(host, "BLOCKED")
            raise RuntimeError(f"Network blocked: {host}. Offline mode is enabled.")
            
        # Even if offline mode is disabled, we might want to block telemetry or cloud APIs
        blocked_domains = [
            "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com",
            "api.cohere.ai", "api.x.ai", "huggingface.co"
        ]
        
        if any(d in host for d in blocked_domains):
            self._log_and_emit(host, "BLOCKED")
            raise RuntimeError(f"Network blocked: Cloud APIs are strictly forbidden ({host}).")
            
        self._log_and_emit(host, "ALLOWED")
        return True
        
    def _log_and_emit(self, host: str, status: str):
        self.logger.log(host, status)
        self.signals.connection_detected.emit(host, status)

# Singleton instance
network_guard = NetworkGuard()
