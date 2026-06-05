import AppKit

class KnowledgeBaseController: NSViewController, NSTableViewDataSource, NSTableViewDelegate {
    
    let scrollView = NSScrollView()
    let tableView = NSTableView()
    
    let refreshBtn = NSButton()
    let deleteBtn = NSButton()
    
    var documents: [APIClient.Document] = []
    
    override func loadView() {
        self.view = NSView(frame: NSRect(x: 0, y: 0, width: 740, height: 620))
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let titleLabel = NSTextField(labelWithString: "Knowledge Base")
        titleLabel.font = NSFont.systemFont(ofSize: 24, weight: .bold)
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(titleLabel)
        
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.hasVerticalScroller = true
        view.addSubview(scrollView)
        
        let column = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("NameColumn"))
        column.title = "Document Name"
        column.width = 660
        tableView.addTableColumn(column)
        
        tableView.dataSource = self
        tableView.delegate = self
        tableView.headerView = nil
        tableView.style = .plain
        tableView.rowHeight = 32
        
        scrollView.documentView = tableView
        
        // Refresh Button
        refreshBtn.title = "  Refresh"
        refreshBtn.image = NSImage(systemSymbolName: "arrow.clockwise", accessibilityDescription: nil)
        refreshBtn.imagePosition = .imageLeft
        refreshBtn.bezelStyle = .rounded
        refreshBtn.target = self
        refreshBtn.action = #selector(loadData)
        refreshBtn.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(refreshBtn)
        
        // Delete Button
        deleteBtn.title = "  Delete"
        deleteBtn.image = NSImage(systemSymbolName: "trash", accessibilityDescription: nil)
        deleteBtn.imagePosition = .imageLeft
        deleteBtn.bezelStyle = .rounded
        deleteBtn.target = self
        deleteBtn.action = #selector(deleteSelected)
        deleteBtn.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(deleteBtn)
        
        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: view.topAnchor, constant: 40),
            titleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 40),
            
            refreshBtn.centerYAnchor.constraint(equalTo: titleLabel.centerYAnchor),
            refreshBtn.trailingAnchor.constraint(equalTo: deleteBtn.leadingAnchor, constant: -10),
            
            deleteBtn.centerYAnchor.constraint(equalTo: titleLabel.centerYAnchor),
            deleteBtn.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -40),
            
            scrollView.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 20),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 40),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -40),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -40)
        ])
        
        loadData()
    }
    
    @objc func loadData() {
        APIClient.shared.listKnowledgeBase { [weak self] docs in
            DispatchQueue.main.async {
                self?.documents = docs
                self?.tableView.reloadData()
            }
        }
    }
    
    @objc func deleteSelected() {
        let row = tableView.selectedRow
        guard row >= 0 && row < documents.count else {
            let alert = NSAlert()
            alert.messageText = "No Selection"
            alert.informativeText = "Please select a document from the list to delete."
            alert.alertStyle = .informational
            alert.addButton(withTitle: "OK")
            alert.runModal()
            return
        }
        
        let doc = documents[row]
        
        let confirmAlert = NSAlert()
        confirmAlert.messageText = "Delete Document?"
        confirmAlert.informativeText = "Are you sure you want to delete \(doc.name)? This will remove it from disk and index."
        confirmAlert.alertStyle = .warning
        confirmAlert.addButton(withTitle: "Delete")
        confirmAlert.addButton(withTitle: "Cancel")
        
        let response = confirmAlert.runModal()
        if response == .alertFirstButtonReturn {
            APIClient.shared.deleteDocument(path: doc.path) { [weak self] success in
                DispatchQueue.main.async {
                    if success {
                        self?.loadData()
                    } else {
                        let alert = NSAlert()
                        alert.messageText = "Error"
                        alert.informativeText = "Could not delete document."
                        alert.alertStyle = .critical
                        alert.addButton(withTitle: "OK")
                        alert.runModal()
                    }
                }
            }
        }
    }
    
    func numberOfRows(in tableView: NSTableView) -> Int {
        return documents.count
    }
    
    func tableView(_ tableView: NSTableView, viewFor tableColumn: NSTableColumn?, row: Int) -> NSView? {
        let container = NSStackView()
        container.orientation = .horizontal
        container.alignment = .centerY
        container.spacing = 8
        
        let icon = NSImageView()
        icon.image = NSImage(systemSymbolName: "doc.text", accessibilityDescription: nil)
        icon.contentTintColor = NSColor.secondaryLabelColor
        icon.imageScaling = .scaleProportionallyUpOrDown
        icon.translatesAutoresizingMaskIntoConstraints = false
        icon.widthAnchor.constraint(equalToConstant: 16).isActive = true
        icon.heightAnchor.constraint(equalToConstant: 16).isActive = true

        
        let text = NSTextField(labelWithString: documents[row].name)
        text.font = NSFont.systemFont(ofSize: 14)
        text.isEditable = false
        text.isBordered = false
        text.backgroundColor = .clear
        
        container.addArrangedSubview(icon)
        container.addArrangedSubview(text)
        return container
    }
}
