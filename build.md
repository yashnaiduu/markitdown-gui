# Build MarkItDown Studio

## Mission

Build a premium macOS-native desktop application called MarkItDown Studio.

The application should feel comparable in quality to Linear, Raycast, Notion, Arc, and modern Apple applications.

The target platform is:

- macOS Sonoma+
- Apple Silicon (M-series)
- Python 3.14+
- PySide6

The application should be production-ready, modular, maintainable, and packaged as a standalone .app.

---

# Core Purpose

MarkItDown Studio is an AI-powered document ingestion, conversion, knowledge management, and RAG platform.

Users should be able to:

- Drop documents
- Paste URLs
- Paste YouTube links
- Convert everything to Markdown using MarkItDown
- Organize converted content automatically
- Build local RAG indexes
- Query knowledge bases using Ollama
- Chat with documents locally

Everything should work offline except external URLs.

---

# Design Requirements

## Visual Style

Create a premium Apple-inspired UI.

Requirements:

- Native macOS feel
- SF Pro typography
- Dark mode
- Light mode
- Theme persistence
- Rounded corners
- Glassmorphism effects where appropriate
- Smooth animations
- Sidebar navigation
- Modern toolbar
- Keyboard shortcuts
- Responsive layouts

Inspiration:

- Linear
- Raycast
- Arc Browser
- Notion
- Apple Settings
- Xcode

---

# Navigation

Sidebar Sections:

1. Dashboard
2. Convert Files
3. Convert URLs
4. YouTube
5. Batch Processing
6. Knowledge Base
7. Search
8. RAG Index
9. AI Chat
10. Logs
11. Settings

---

# Dashboard

Display:

- Total documents
- Total markdown files
- Total indexed chunks
- Vector DB size
- Recent conversions
- Recent searches
- Active AI model

Include:

- Quick Actions
- Convert File
- Paste URL
- Paste YouTube
- Build Index
- Open Knowledge Base

---

# File Conversion

Support drag-and-drop.

Accept:

- PDF
- DOCX
- PPTX
- XLSX
- HTML
- CSV
- JSON
- XML
- EPUB
- TXT
- MD

Features:

- Multi-file conversion
- Folder conversion
- Recursive folder scanning
- Progress tracking
- Cancellation
- Retry failed files

Use MarkItDown CLI internally.

---

# URL Conversion

User pastes:

- Website URL
- Direct PDF URL
- Documentation URL

Features:

- Auto-detect URL type
- Convert to Markdown
- Save source metadata
- Preserve source URL

---

# YouTube Conversion

User pastes:

- YouTube URL

Features:

- Fetch transcript using MarkItDown
- Save transcript as Markdown
- Save metadata:
  - title
  - channel
  - URL
  - date

Allow:

- Batch YouTube imports

---

# Batch Processing

Features:

- Select folder
- Recursive scan
- Queue management
- Pause
- Resume
- Cancel
- Progress bars
- Parallel processing

Should handle thousands of files.

---

# Knowledge Base

Directory structure:

knowledge_base/
├── markdown/
├── urls/
├── youtube/
├── uploads/
├── chroma/
├── embeddings/
├── logs/
└── exports/

Features:

- Browse documents
- Open markdown preview
- Search filenames
- Tag documents
- Delete documents
- Re-index documents

---

# Markdown Viewer

Features:

- Syntax highlighting
- Live preview
- Search within document
- Export options

---

# ChromaDB Integration

Use:

- chromadb

Features:

- Persistent database
- Automatic indexing
- Rebuild index
- Delete vectors
- Collection management

---

# Embeddings

Use:

- sentence-transformers

Default model:

all-MiniLM-L6-v2

Allow changing embedding model in settings.

---

# RAG Pipeline

Workflow:

Document
→ Markdown
→ Chunking
→ Embeddings
→ ChromaDB
→ Retrieval
→ Ollama

Chunk settings:

- configurable chunk size
- configurable overlap

---

# Search

Provide semantic search.

User enters query.

System:

- Generates embedding
- Searches ChromaDB
- Displays relevant chunks

Show:

- source file
- score
- preview

---

# Ollama Integration

Use local Ollama installation.

Detect installed models automatically.

Support:

- qwen3
- llama3
- gemma3
- mistral

Features:

- model selection
- streaming responses
- temperature control
- context window settings

---

# AI Chat

Modes:

1. Normal Chat
2. RAG Chat

Normal Chat:

User chats directly with Ollama.

RAG Chat:

User chats with indexed knowledge base.

Features:

- streaming tokens
- markdown rendering
- code blocks
- citations
- source references

---

# Settings

Persist using QSettings.

Configurable:

- Theme
- Output folder
- Knowledge base location
- Chunk size
- Chunk overlap
- Embedding model
- Ollama model
- Auto-index toggle
- Auto-convert toggle

---

# Logging

Create structured logs.

Store:

knowledge_base/logs/

Log:

- conversions
- indexing
- searches
- chat sessions
- errors

---

# Architecture

Use clean architecture.

Folders:

ui/
core/
services/
workers/
models/
storage/

Keep UI separated from business logic.

Use dependency injection where possible.

---

# Concurrency

Use:

- QThread
- QRunnable
- QThreadPool

Never block UI.

All conversions and indexing must run in background workers.

---

# Packaging

Support:

- PyInstaller

Generate:

MarkItDown Studio.app

Requirements:

- standalone
- signed-ready
- production-ready

---

# Quality Requirements

Code must:

- be typed
- use docstrings
- follow PEP8
- include error handling
- include logging
- include unit-test-ready architecture

Avoid placeholders.

Implement working code.

Generate all required modules, classes, workers, services, UI components, settings managers, themes, and integrations.

# Privacy and Local-Only Requirements (Mandatory)

This application must be 100% local-first.

No user data may leave the machine unless the user explicitly imports a URL or YouTube link.

## Local Execution Only

All processing must occur locally:

- MarkItDown
- ChromaDB
- Embeddings
- Ollama
- Search
- RAG
- AI Chat
- Knowledge Base

No cloud APIs.

No SaaS services.

No telemetry.

No analytics.

No tracking.

No crash reporting.

No usage statistics.

No background network communication.

No external authentication.

No accounts.

No subscriptions.

No API keys.

No login system.

## Allowed Network Activity

The application may only access the network when the user explicitly requests:

- Convert a URL
- Convert a website
- Convert a PDF URL
- Convert a YouTube URL
- Check for application updates (optional and disabled by default)

All other functionality must work fully offline.

## AI Requirements

Use only local models through Ollama.

Supported examples:

- qwen3
- llama3
- gemma3
- mistral

Never call:

- OpenAI API
- Anthropic API
- Gemini API
- Grok API
- Cohere API
- Hugging Face Inference API
- Any remote LLM service

All inference must occur on-device.

## Embeddings

Generate embeddings locally using:

- sentence-transformers

Store embeddings locally.

Never upload embeddings.

## Vector Database

Use:

- ChromaDB PersistentClient

Store database only on local disk.

No remote vector stores.

No cloud synchronization.

## Security

Provide a setting:

"Offline Mode"

When enabled:

- Block all outbound network requests
- Disable URL imports
- Disable YouTube imports
- Disable update checks

Allow operation entirely without internet access.

## Data Storage

All application data must be stored under:

knowledge_base/

including:

- markdown
- embeddings
- vector database
- logs
- settings

No cloud backup.

No remote storage.

## Packaging

Application must run entirely offline after installation.

No dependency on external services.

The app should remain fully functional without an internet connection.

Settings
├── General
├── Appearance
├── AI Models
├── Knowledge Base
├── Privacy
└── Advanced


────────────────────────────
Privacy & Network Control
────────────────────────────

[✓] Offline Mode (Default ON)

Status:
● No Network Activity

Outbound Connections Today:
0

Blocked Requests:
0

Allowed Requests:
0

────────────────────────────

Network Activity Log

Time        Action        Host
--------------------------------
14:22       BLOCKED       youtube.com
14:25       ALLOWED       docs.python.org

────────────────────────────

[Clear Log]
[Export Log]


Offline Mode Behavior

When enabled:
OFFLINE_MODE = True

The app should block:

* HTTP requests
* HTTPS requests
* WebSockets
* Automatic update checks
* URL imports
* YouTube imports

Only local operations remain available:

* MarkItDown on local files
* ChromaDB
* Ollama
* RAG
* Search
* Chat

⸻

Network Guard

Create:
core/security/
├── network_guard.py
├── connection_logger.py
└── privacy_manager.py

network_guard.py

All network operations must go through this layer.

Example:
class NetworkGuard:

    def __init__(self, offline_mode):

        self.offline_mode = offline_mode

    def check(self, host):

        if self.offline_mode:
            raise RuntimeError(
                f"Network blocked: {host}"
            )

        return True

Connection Logger

Every network attempt gets logged.
{
    "time": "...",
    "host": "youtube.com",
    "action": "BLOCKED"
}

Stored locally:
knowledge_base/logs/network.log

Real-Time Monitor

Whenever a connection is attempted:

connection_detected.emit(
    host,
    status
)

connection_detected.emit(
    host,
    status
)

The Settings page updates live.
Host            Status
──────────────────────
youtube.com     BLOCKED
github.com      BLOCKED


Startup Verification

On launch:

Privacy Check

✓ Offline Mode Enabled
✓ Ollama Local
✓ ChromaDB Local
✓ No Cloud APIs Configured
✓ Telemetry Disabled

System Secure

⸻

AI Provider Validation

The app should scan configuration and warn if a cloud provider is configured.

Detect:

* OpenAI
* Anthropic
* Gemini
* Grok
* Cohere

Example:
Warning

OpenAI API key detected.

This application is configured
for local-only operation.

[Remove Key]
[Ignore]


Security Dashboard

Add a dashboard card:

Privacy Status

🟢 Local Only

Network Requests:
0

Cloud Providers:
0

Telemetry:
Disabled

Offline Mode:
Enabled

Advanced Protection

For maximum confidence, tell your Codex agent to implement:

1. Single network abstraction layer (NetworkGuard) that all network code must use.
2. Default Offline Mode = ON.
3. No telemetry code anywhere in the project.
4. No analytics SDKs.
5. No crash-reporting services.
6. Privacy audit page showing:
    * Active sockets
    * Recent connections
    * Allowed requests
    * Blocked requests
7. Export privacy report to Markdown or JSON.
