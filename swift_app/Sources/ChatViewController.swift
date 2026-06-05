import AppKit

class ChatViewController: NSViewController, NSTextFieldDelegate {
    
    let chatLog = NSTextView()
    let scrollView = NSScrollView()
    let inputField = NSTextField()
    
    let sendButton = NSButton()
    let clearButton = NSButton()
    let ragCheckbox = NSButton(checkboxWithTitle: "Use RAG Context", target: nil, action: nil)
    
    // Store chat history locally to keep conversation continuity
    var history: [[String: String]] = []
    
    override func loadView() {
        self.view = NSView(frame: NSRect(x: 0, y: 0, width: 740, height: 620))
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Title Label
        let titleLabel = NSTextField(labelWithString: "AI Chat")
        titleLabel.font = NSFont.systemFont(ofSize: 24, weight: .bold)
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(titleLabel)
        
        // Clear Chat Button (Top Right)
        clearButton.title = "  Clear"
        clearButton.image = NSImage(systemSymbolName: "trash", accessibilityDescription: nil)
        clearButton.imagePosition = .imageLeft
        clearButton.bezelStyle = .rounded
        clearButton.target = self
        clearButton.action = #selector(clearChat)
        clearButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(clearButton)
        
        // Chat Log Scroll View
        chatLog.isEditable = false
        chatLog.font = NSFont.systemFont(ofSize: 14)
        chatLog.backgroundColor = NSColor.textBackgroundColor
        
        scrollView.documentView = chatLog
        scrollView.hasVerticalScroller = true
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scrollView)
        
        // RAG Checkbox
        ragCheckbox.state = .on
        ragCheckbox.font = NSFont.systemFont(ofSize: 13, weight: .regular)
        ragCheckbox.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(ragCheckbox)
        
        // Message Input Field
        inputField.placeholderString = "Ask something about your Knowledge Base..."
        inputField.delegate = self
        inputField.font = NSFont.systemFont(ofSize: 14)
        inputField.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(inputField)
        
        // Send Button
        sendButton.title = ""
        sendButton.image = NSImage(systemSymbolName: "paperplane.fill", accessibilityDescription: "Send")
        sendButton.bezelStyle = .rounded
        sendButton.target = self
        sendButton.action = #selector(sendMessage)
        sendButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(sendButton)
        
        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: view.topAnchor, constant: 40),
            titleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 40),
            
            clearButton.centerYAnchor.constraint(equalTo: titleLabel.centerYAnchor),
            clearButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -40),
            
            scrollView.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 20),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 40),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -40),
            scrollView.bottomAnchor.constraint(equalTo: ragCheckbox.topAnchor, constant: -10),
            
            ragCheckbox.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 40),
            ragCheckbox.bottomAnchor.constraint(equalTo: inputField.topAnchor, constant: -8),
            
            inputField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 40),
            inputField.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -40),
            inputField.heightAnchor.constraint(equalToConstant: 32),
            
            sendButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -40),
            sendButton.centerYAnchor.constraint(equalTo: inputField.centerYAnchor),
            sendButton.leadingAnchor.constraint(equalTo: inputField.trailingAnchor, constant: 10),
            sendButton.widthAnchor.constraint(equalToConstant: 60),
            sendButton.heightAnchor.constraint(equalToConstant: 32)
        ])
        
        appendMessage("AI: Hello! How can I assist you with your knowledge base documents today?")
    }
    
    func appendMessage(_ text: String) {
        let attrString = NSAttributedString(string: text + "\n\n", attributes: [.font: NSFont.systemFont(ofSize: 14)])
        chatLog.textStorage?.append(attrString)
        chatLog.scrollToEndOfDocument(nil)
    }
    
    @objc func clearChat() {
        history.removeAll()
        chatLog.string = ""
        appendMessage("AI: Chat history cleared. Ask me anything!")
    }
    
    @objc func sendMessage() {
        let text = inputField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        
        appendMessage("You: \(text)")
        inputField.stringValue = ""
        
        let useRAG = ragCheckbox.state == .on
        
        inputField.isEnabled = false
        sendButton.isEnabled = false
        
        APIClient.shared.chat(prompt: text, useRAG: useRAG, history: history) { [weak self] response in
            DispatchQueue.main.async {
                self?.inputField.isEnabled = true
                self?.sendButton.isEnabled = true
                self?.inputField.window?.makeFirstResponder(self?.inputField)
                
                if let response = response {
                    self?.appendMessage("AI: \(response)")
                    self?.history.append(["role": "user", "content": text])
                    self?.history.append(["role": "assistant", "content": response])
                } else {
                    self?.appendMessage("AI: Error generating response. Check local Ollama connection.")
                }
            }
        }
    }
    
    func control(_ control: NSControl, textView: NSTextView, doCommandBy commandSelector: Selector) -> Bool {
        if commandSelector == #selector(insertNewline(_:)) {
            sendMessage()
            return true
        }
        return false
    }
}
