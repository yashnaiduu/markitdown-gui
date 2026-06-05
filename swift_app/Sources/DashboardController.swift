import AppKit

class DashboardController: NSViewController {
    
    let sidebar = NSStackView()
    let contentView = NSView()
    
    // Sub-controllers
    let kbController = KnowledgeBaseController()
    let chatController = ChatViewController()
    
    // Track current active controller
    var currentContentController: NSViewController?
    
    override func loadView() {
        self.view = NSView(frame: NSRect(x: 0, y: 0, width: 960, height: 620))
        self.view.wantsLayer = true
        self.view.layer?.backgroundColor = NSColor.windowBackgroundColor.cgColor
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        setupSidebar()
        setupContentView()
        
        // Show KB by default
        switchTo(controller: kbController)
    }
    
    func setupSidebar() {
        sidebar.orientation = .vertical
        sidebar.alignment = .leading
        sidebar.spacing = 14
        sidebar.edgeInsets = NSEdgeInsets(top: 40, left: 20, bottom: 20, right: 20)
        sidebar.wantsLayer = true
        sidebar.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        sidebar.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(sidebar)
        
        let title = NSTextField(labelWithString: "MarkItDown Studio")
        title.font = NSFont.systemFont(ofSize: 18, weight: .bold)
        sidebar.addArrangedSubview(title)
        
        sidebar.addArrangedSubview(NSView(frame: NSRect(x: 0, y: 0, width: 0, height: 10))) // Spacer
        
        // 1. Knowledge Base button
        let kbBtn = NSButton(title: "  Knowledge Base", target: self, action: #selector(showKB))
        kbBtn.image = NSImage(systemSymbolName: "books.vertical.fill", accessibilityDescription: nil)
        kbBtn.imagePosition = .imageLeft
        kbBtn.bezelStyle = .recessed
        kbBtn.isBordered = false
        kbBtn.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        sidebar.addArrangedSubview(kbBtn)
        
        // 2. Chat Button
        let chatBtn = NSButton(title: "  AI Chat", target: self, action: #selector(showChat))
        chatBtn.image = NSImage(systemSymbolName: "sparkles", accessibilityDescription: nil)
        chatBtn.imagePosition = .imageLeft
        chatBtn.bezelStyle = .recessed
        chatBtn.isBordered = false
        chatBtn.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        sidebar.addArrangedSubview(chatBtn)

        
        sidebar.addArrangedSubview(NSView(frame: NSRect(x: 0, y: 0, width: 0, height: 30))) // Spacer
        
        // 3. Collapse/Shrink Button
        let shrinkBtn = NSButton(title: "  Collapse to Drop Zone", target: self, action: #selector(shrinkToDropZone))
        shrinkBtn.image = NSImage(systemSymbolName: "arrow.down.right.and.arrow.up.left", accessibilityDescription: nil)
        shrinkBtn.imagePosition = .imageLeft
        shrinkBtn.bezelStyle = .rounded
        shrinkBtn.font = NSFont.systemFont(ofSize: 12)
        sidebar.addArrangedSubview(shrinkBtn)
        
        NSLayoutConstraint.activate([
            sidebar.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            sidebar.topAnchor.constraint(equalTo: view.topAnchor),
            sidebar.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            sidebar.widthAnchor.constraint(equalToConstant: 220)
        ])
    }
    
    func setupContentView() {
        contentView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(contentView)
        
        NSLayoutConstraint.activate([
            contentView.leadingAnchor.constraint(equalTo: sidebar.trailingAnchor),
            contentView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            contentView.topAnchor.constraint(equalTo: view.topAnchor),
            contentView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }
    
    @objc func showKB() {
        switchTo(controller: kbController)
    }
    
    @objc func showChat() {
        switchTo(controller: chatController)
    }
    
    func switchTo(controller: NSViewController) {
        currentContentController?.view.removeFromSuperview()
        currentContentController?.removeFromParent()
        
        addChild(controller)
        controller.view.frame = contentView.bounds
        controller.view.autoresizingMask = [.width, .height]
        contentView.addSubview(controller.view)
        
        currentContentController = controller
        
        // Refresh subviews dynamically if they support it
        if let kb = controller as? KnowledgeBaseController {
            kb.loadData()
        }
    }
    
    @objc func shrinkToDropZone() {
        guard let window = self.view.window else { return }
        let newSize = NSSize(width: 250, height: 250)
        var frame = window.frame
        let oldCenter = NSPoint(x: frame.midX, y: frame.midY)
        
        frame.size = newSize
        frame.origin.x = oldCenter.x - (newSize.width / 2)
        frame.origin.y = oldCenter.y - (newSize.height / 2)
        
        NSAnimationContext.runAnimationGroup({ context in
            context.duration = 0.4
            context.timingFunction = CAMediaTimingFunction(controlPoints: 0.2, 0.8, 0.2, 1.0)
            window.animator().setFrame(frame, display: true)
        }) {
            let dropZone = DropZoneController()
            window.contentViewController = dropZone
        }
    }
}
