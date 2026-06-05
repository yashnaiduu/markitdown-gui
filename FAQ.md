# Frequently Asked Questions (FAQ)

Welcome to the MarkItDown Studio FAQ! If you can't find the answer to your question here, feel free to [open an issue](https://github.com/yashnaiduu/markitdown-gui/issues/new/choose) or start a discussion.

## 📖 General

### What is the difference between MarkItDown and MarkItDown Studio?
[MarkItDown](https://github.com/microsoft/markitdown) is a fantastic, open-source Python utility developed by Microsoft for converting various file formats to Markdown. **MarkItDown Studio** is an independent, community-driven desktop graphical user interface (GUI) built on top of that utility. It provides a native macOS experience, seamless local LLM chat, and a built-in knowledge base, making document processing accessible without touching the command line.

### Is MarkItDown Studio free?
Yes! MarkItDown Studio is completely open-source and free to use under the MIT License.

## 🔒 Privacy & Security

### Do my documents ever leave my computer?
**No.** MarkItDown Studio is designed with a privacy-first approach. All document conversions happen locally on your machine. If you use the local LLM integration via Ollama, your chat interactions and document analysis also remain 100% offline. 

If you are converting web URLs or YouTube videos, the application will naturally need to access the internet to fetch that content, but your local files are never uploaded anywhere.

### What is "Strict Offline Mode"?
In the Settings panel, you can enable **Strict Offline Mode**. This engages an internal network guard that blocks any accidental outbound network requests during document parsing, ensuring zero data leakage in highly secure environments.

## ⚙️ Installation & Usage

### How do I install the core MarkItDown dependency?
We've made this incredibly easy. Simply open MarkItDown Studio, navigate to the **Settings** tab, scroll down to the **Dependencies & Tools** section, and click **Install MarkItDown**. The app will handle the `pip` installation for you in the background.

### Why do I need to restart the app after installing the dependency?
Because Python loads libraries into memory when the application starts, it cannot immediately recognize newly installed packages on the fly. Restarting the application ensures the Python interpreter cleanly imports the freshly installed core utilities.

### What file formats are currently supported?
MarkItDown Studio inherits its robust parsing capabilities from the core utility. Currently supported formats include:
- PDFs (`.pdf`)
- Word Documents (`.docx`)
- PowerPoint Presentations (`.pptx`)
- Excel Spreadsheets (`.xlsx`)
- Images (with local OCR support)
- Text-based formats (`.csv`, `.json`, `.xml`, `.html`)
- YouTube URLs and standard Web Pages

## 🤖 AI & Local LLMs

### How do I use the local chat feature?
To chat with your documents locally:
1. Download and install [Ollama](https://ollama.com/).
2. Pull a model using your terminal (e.g., `ollama run llama3`).
3. Open MarkItDown Studio, go to **Settings**, and select your downloaded model from the dropdown.
4. Head to the **Chat** tab and start asking questions!

### Can I use OpenAI or Anthropic instead of Ollama?
Currently, MarkItDown Studio is strictly optimized for local, privacy-preserving setups using Ollama. However, an extensible plugin system to support cloud providers is on our roadmap. If you'd like to see this sooner, PRs are welcome!

### What are Chunk Size and Overlap in the settings?
When you add a large document to your Knowledge Base, the app breaks it down into smaller "chunks" so the AI can efficiently search and retrieve relevant information. 
- **Chunk Size** is the maximum number of characters in a single chunk.
- **Chunk Overlap** is the number of characters shared between consecutive chunks to ensure context isn't lost between boundaries.

## 🛠 Troubleshooting

### The app crashes when I try to build the macOS version.
Ensure you have Xcode Command Line Tools installed. You can install them by running `xcode-select --install` in your terminal. Also, verify that your Python virtual environment is activated before running `./build_mac.sh`.

### My documents aren't converting correctly.
Double-check that the file isn't password-protected or corrupted. If it's a scanned PDF, ensure you have an active Ollama model selected in Settings that supports vision capabilities (like `llava`) for the OCR to work.
