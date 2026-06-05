#!/bin/bash
echo "Building MarkItDown Studio for macOS..."

# Ensure we are in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Clean previous builds
rm -rf build/ dist/

# Run PyInstaller using the existing spec file
pyinstaller --noconfirm --clean "MarkItDown Studio.spec"

echo "Build complete! Application is in the 'dist' directory."
