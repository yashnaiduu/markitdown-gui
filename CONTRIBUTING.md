# Contributing to MarkItDown Studio

First off, thank you for considering contributing to MarkItDown Studio! It's people like you that make open source such a great community.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/yashnaiduu/markitdown-gui/issues) to see if someone else has already created a ticket. If not, go ahead and make one!

## Fork & create a branch

If this is something you think you can fix, then fork MarkItDown Studio and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```bash
git checkout -b 325-add-pdf-password-support
```

## Local Development Setup

1. **Fork the repo** and clone it locally.
2. **Set up your Python environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run the application** to verify your setup:
   ```bash
   python main.py
   ```

## Pull Request Guidelines

When you're ready to submit a pull request, please make sure:
- You fill out the provided Pull Request Template.
- Your code follows standard Python conventions (PEP 8).
- You have tested your changes thoroughly.
- Your commits are descriptive and explain the "why" not just the "what".

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
