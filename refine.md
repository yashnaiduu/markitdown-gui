# MARKITDOWN_STUDIO_STABILIZATION_SPRINT.md

# Objective

Transform MarkItDown Studio from a functional hackathon prototype into a production-quality application suitable for YC Hackathon demonstrations, open-source adoption, and GSOC-level engineering standards.

The primary goal is reliability, consistency, and complete functionality of every visible feature.

---

# Core Principle

No visible feature should exist in the UI unless it is fully functional.

Every button, menu item, panel, action, and workflow must work end-to-end.

Remove, disable, or hide incomplete functionality until it is production ready.

---

# Golden User Flow

The following workflow must function flawlessly:

1. User uploads file
2. File begins processing
3. Processing progress is displayed
4. Markdown result is generated
5. Result can be previewed
6. Result can be copied
7. Result can be downloaded
8. Result persists after application restart
9. User can chat with result
10. User receives useful AI responses

No failures are acceptable in this workflow.

---

# Phase 1 - Full System Audit

Perform a complete audit of:

* Frontend
* Backend
* Storage
* Processing pipeline
* Ollama integration
* RAG pipeline
* URL conversion
* Knowledge base
* Swift desktop wrapper

Generate a report containing:

* Broken features
* Incomplete features
* Dead buttons
* Missing routes
* Missing event handlers
* Missing state updates
* Missing persistence logic
* Missing error handling

---

# Phase 2 - File Processing Reliability

Investigate entire file lifecycle.

Verify:

Upload
→ Queue
→ Processing
→ Result Creation
→ Storage
→ UI Update
→ Preview
→ Download

For every processed file ensure:

* unique id
* original filename
* output filename
* markdown content
* creation timestamp
* storage path
* download path
* preview path
* processing status

Verify all are present.

No placeholder objects allowed.

---

# Phase 3 - Expanded View Bug Investigation

Current symptom:

Processed files appear inside UI.

However:

* clicking does nothing
* preview fails
* download fails

Investigate:

* click handlers
* routing
* file references
* state synchronization
* storage references

Verify every rendered file card contains valid backing data.

If a file appears in UI it must:

* open
* preview
* copy
* download

without exception.

---

# Phase 4 - Download System

Audit entire download subsystem.

Verify:

* output path exists
* file exists on disk
* permissions correct
* UI references correct endpoint

Add validation:

Before download button appears:

confirm file exists.

If file missing:

show error state.

Never show downloadable files that do not exist.

---

# Phase 5 - Preview System

All processed files must support preview.

Requirements:

Markdown:

* rendered preview

Text:

* rendered preview

HTML:

* rendered preview

Images:

* image preview

PDF:

* preview when possible

Preview must never crash application.

Fallback message required for unsupported formats.

---

# Phase 6 - URL Conversion

Current reports indicate URL conversion visibility issues.

Audit:

* URL import screen
* Link drop zone
* Paste URL flow
* Context menu access
* Toolbar access

Verify users can:

1. Paste URL
2. Submit URL
3. Download content
4. Convert content
5. Preview markdown
6. Save result

No hidden functionality.

No inaccessible screens.

---

# Phase 7 - YouTube Conversion

Verify:

* URL validation
* download pipeline
* transcript extraction
* markdown generation
* storage
* preview

Add meaningful error messages.

Do not silently fail.

---

# Phase 8 - AI Chat Reliability

Current reports indicate AI chat may be broken.

Audit:

Frontend:

* input
* send button
* streaming
* chat history

Backend:

* request handling
* model loading
* response generation

Ollama:

* connectivity
* model discovery
* timeout handling

Verify:

User sends message.

System responds.

Conversation history persists.

---

# Phase 9 - Ollama Integration

Create startup validation.

On application launch:

Check:

* Ollama installed
* Ollama running
* model available

Display status indicators:

Green:
Ready

Yellow:
Partial functionality

Red:
Unavailable

Never allow silent failures.

---

# Phase 10 - Knowledge Base Reliability

Audit:

* indexing
* chunking
* embeddings
* retrieval
* document references

Verify:

Uploaded document appears in knowledge base.

Retrieved chunks correspond to actual documents.

Responses cite source documents.

No hallucinated references.

---

# Phase 11 - State Management Audit

Search entire codebase for:

temporary state
placeholder state
duplicate state

Ensure:

single source of truth.

Prevent:

UI displaying data that backend cannot provide.

Prevent:

backend data existing but UI not updating.

---

# Phase 12 - Error Handling

Every operation requires:

Loading
Success
Failure

states.

Never allow silent failures.

Examples:

Upload failed.

Download failed.

Model unavailable.

Conversion failed.

Storage unavailable.

Network unavailable.

Display actionable error messages.

---

# Phase 13 - Logging

Implement structured logging.

Log:

uploads
conversions
downloads
chat requests
RAG requests
errors

Every critical action must be traceable.

---

# Phase 14 - UX Consistency

Audit all screens.

Requirements:

consistent spacing

consistent typography

consistent button behavior

consistent icons

consistent status indicators

consistent naming

No mixed design patterns.

---

# Phase 15 - Loading States

Every asynchronous operation must show progress.

Examples:

Uploading...
Processing...
Generating Markdown...
Indexing...
Querying Knowledge Base...
Generating Response...

No frozen interfaces.

---

# Phase 16 - Persistence

Verify persistence across restart.

Application restart must preserve:

documents

conversions

knowledge base

chat history

settings

preferences

No accidental data loss.

---

# Phase 17 - Desktop App Validation

Audit Swift wrapper.

Verify:

window management

file dialogs

drag and drop

native menus

backend communication

packaging

startup

shutdown

No broken macOS integration.

---

# Phase 18 - Security Review

Validate:

file paths

temporary files

URL imports

external content

command execution

input validation

Prevent:

path traversal

unsafe file execution

malicious document handling

---

# Phase 19 - Performance

Test with:

10 files

50 files

100 files

large PDFs

large DOCX

large PowerPoints

large knowledge bases

Ensure application remains responsive.

---

# Phase 20 - Demo Readiness

Before release verify:

✓ Upload works

✓ Conversion works

✓ Preview works

✓ Download works

✓ URL conversion works

✓ YouTube conversion works

✓ Ollama works

✓ Chat works

✓ Knowledge base works

✓ Persistence works

✓ No dead buttons

✓ No console errors

✓ No uncaught exceptions

✓ No broken navigation

✓ No inaccessible features

---

# Final Acceptance Criteria

A user with no prior knowledge should be able to:

1. Install application
2. Launch application
3. Upload file
4. Convert file
5. Preview markdown
6. Download markdown
7. Ask AI questions
8. Build knowledge base
9. Query knowledge base
10. Use URL conversion

without encountering a single broken workflow.

If any visible feature fails, the release is not ready.

# Phase 21 - Native macOS Menu Bar Integration

MarkItDown Studio must behave like a first-class native macOS application.

Users should be able to control the application through the standard macOS menu bar and application menu.

---

## Application Menu Requirements

Implement a native application menu containing:

MarkItDown Studio

* About MarkItDown Studio
* Check for Updates
* Preferences...
* Services
* Hide MarkItDown Studio
* Hide Others
* Show All
* Quit MarkItDown Studio

All menu items must be functional.

No placeholder entries.

---

## Menu Bar Actions

Required actions:

### About

Displays:

* application version
* build number
* GitHub repository
* license information

---

### Check For Updates

Provide:

* manual update check
* current version display
* latest version display
* update availability status

If update exists:

Display:

Update Available

Allow:

* download update
* install update
* restart application

---

### Restart To Update

If update downloaded:

Display:

Restart to Update

Selecting it must:

1. close running services
2. save application state
3. restart application
4. launch updated version

---

### Preferences

Preferences window must include:

General

* launch at startup
* theme selection
* notifications

Conversion

* output directory
* default export format
* overwrite behavior

AI

* Ollama endpoint
* default model
* temperature
* context window

Knowledge Base

* storage location
* embedding model
* chunk size
* retrieval count

Advanced

* logs
* cache
* diagnostics
* reset application

---

### Quit

Quit must:

* save application state
* stop background workers
* close Ollama connections
* release resources
* exit cleanly

No force termination.

No orphan processes.

---

# Phase 22 - Native Keyboard Shortcuts

All standard macOS shortcuts must function correctly.

Failure of standard shortcuts is unacceptable.

---

## Global Application Shortcuts

Required:

Command + Q
Quit Application

Command + W
Close Window

Command + M
Minimize Window

Command + H
Hide Application

Command + Option + H
Hide Others

Command + ,
Open Preferences

Command + N
New Session

Command + O
Open File

Command + Shift + O
Open Folder

Command + R
Refresh Current View

Command + Shift + R
Reprocess Current Document

---

## Editing Shortcuts

Required:

Command + A
Select All

Command + C
Copy

Command + X
Cut

Command + V
Paste

Command + Z
Undo

Command + Shift + Z
Redo

Command + F
Find

Command + G
Find Next

---

## Document Shortcuts

Required:

Space
Quick Preview

Enter
Open Selected Document

Delete
Remove Selected Document

Command + D
Download Selected Document

Command + Shift + D
Duplicate Document

---

## AI Chat Shortcuts

Required:

Enter
Send Message

Shift + Enter
New Line

Command + K
Focus AI Chat

Command + L
Clear Chat

Command + Enter
Regenerate Response

---

## Knowledge Base Shortcuts

Required:

Command + I
Index Documents

Command + Shift + I
Reindex Knowledge Base

Command + B
Open Knowledge Base

---

# Phase 23 - Native Menu Bar Status Item

Implement optional macOS status bar item.

Display application icon in top menu bar.

Menu should contain:

Open MarkItDown Studio

Recent Documents

Recent Conversions

Check For Updates

Preferences

Diagnostics

Quit

---

# Phase 24 - Native Window Management

Application windows must follow macOS conventions.

Support:

* full screen mode
* split view
* window restoration
* multiple windows
* tabbed windows

Persist window state between launches.

---

# Phase 25 - Auto Update System

Implement production-grade update workflow.

Requirements:

* update checks on launch
* manual update checks
* background update downloads
* update notifications
* restart and install

Support:

GitHub Releases

or

Sparkle Framework

preferred for macOS.

---

# Phase 26 - macOS Human Interface Guidelines Compliance

Audit entire UI against Apple's Human Interface Guidelines.

Verify:

* spacing
* typography
* animations
* window behavior
* menus
* dialogs
* alerts
* shortcuts

The application should feel indistinguishable from a professionally built native macOS application.

---

# Phase 27 - Native Desktop Quality Benchmark

MarkItDown Studio should meet or exceed the UX quality level of:

* Ollama Desktop
* Raycast
* Notion Desktop
* Linear
* Obsidian
* Arc Browser

Evaluation Criteria:

✓ Native menus

✓ Native shortcuts

✓ Native window behavior

✓ Update system

✓ Menu bar integration

✓ Preferences panel

✓ Smooth animations

✓ Reliable file handling

✓ Reliable AI chat

✓ No dead UI elements

✓ No broken workflows

✓ No console errors

✓ No uncaught exceptions

✓ No shortcut failures

Release is blocked until all criteria are satisfied.
