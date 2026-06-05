# MarkItDown Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![macOS](https://img.shields.io/badge/os-macOS-green.svg)]()

> [!IMPORTANT]
> MarkItDown Studio performs I/O with the privileges of the current process. It is a desktop application providing a rich user interface for document conversion and querying. Ensure you trust the documents you process and the models you interact with.

> **Note:** This is an independent, community-driven project built by an individual developer. It is **not** affiliated with or officially endorsed by Microsoft. It acts as a desktop GUI built on top of Microsoft's fantastic [MarkItDown](https://github.com/microsoft/markitdown) utility.

MarkItDown Studio is a powerful, modern GUI built around the concept of converting various file formats to Markdown for use with LLMs and knowledge bases. It provides an intuitive desktop experience for document processing, chatting with local models via Ollama, and maintaining an intelligent knowledge base.

It supports all the formats that standard markdown converters do, wrapped in a beautiful, native-feeling macOS interface with both Python and Swift components.

## Features

- **Drag and Drop Conversion**: Easily convert PDFs, Word docs, Excel, PowerPoint, and images to clean Markdown.
- **Local LLM Integration**: Chat with your documents completely offline using Ollama.
- **Knowledge Base**: Store your converted documents, index them, and use RAG (Retrieval-Augmented Generation) to ask questions across your personal library.
- **URL Conversion**: Download and convert web pages or YouTube videos directly into Markdown.
- **Cross-Platform Foundation**: Core logic in Python with a beautiful desktop GUI.

## Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.com/) (installed and running for local LLM features)
- macOS (for the Swift-based native app components)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yashnaiduu/markitdown-gui.git
   cd markitdown-gui
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Python Application

Start the main Python server/GUI:
```bash
python main.py
```

### Building the macOS Native App

You can build the native macOS experience using the provided build script:
```bash
./build_mac.sh
```

This will package the Python backend and the Swift frontend into a standalone `.app` bundle.

## Architecture

MarkItDown Studio uses a hybrid architecture:
- **Core Processing (`core/`, `services/`, `workers/`)**: Handles file conversions, RAG pipelines, LLM interactions, and background tasks.
- **Storage (`storage/`)**: Vector databases and knowledge base management.
- **User Interface (`ui/`, `swift_app/`)**: A rich frontend experience, blending Python-based UI components with a native macOS Swift application container.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started, set up your development environment, and submit pull requests.

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
