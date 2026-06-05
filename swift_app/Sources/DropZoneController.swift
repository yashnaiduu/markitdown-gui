import AppKit

class DropZoneController: NSViewController {
    let iconView = NSImageView()
    let statusLabel = NSTextField(labelWithString: "Drop file here")
    let expandButton = NSButton()
    let progressIndicator = NSProgressIndicator()
    
    override func loadView() {
        let dropView = DropZoneView(frame: NSRect(x: 0, y: 0, width: 250, height: 250))
        dropView.controller = self
        self.view = dropView
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Setup Icon View with SF Symbol
        iconView.image = NSImage(systemSymbolName: "arrow.down.doc.fill", accessibilityDescription: "Drop files here")
        iconView.contentTintColor = NSColor.secondaryLabelColor
        iconView.imageScaling = .scaleProportionallyUpOrDown
        iconView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(iconView)
        
        // Setup Status Label
        statusLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        statusLabel.textColor = NSColor.secondaryLabelColor
        statusLabel.alignment = .center
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(statusLabel)
        
        // Setup Progress Indicator
        progressIndicator.style = .spinning
        progressIndicator.isIndeterminate = true
        progressIndicator.doubleValue = 0.0
        progressIndicator.translatesAutoresizingMaskIntoConstraints = false
        progressIndicator.isHidden = true
        view.addSubview(progressIndicator)
        
        // Setup Expand Button
        expandButton.title = "Show Studio"
        expandButton.bezelStyle = .rounded
        expandButton.target = self
        expandButton.action = #selector(expandToDashboard)
        expandButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(expandButton)
        
        NSLayoutConstraint.activate([
            iconView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            iconView.centerYAnchor.constraint(equalTo: view.centerYAnchor, constant: -20),
            iconView.widthAnchor.constraint(equalToConstant: 64),
            iconView.heightAnchor.constraint(equalToConstant: 64),
            
            statusLabel.topAnchor.constraint(equalTo: iconView.bottomAnchor, constant: 10),
            statusLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            statusLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 10),
            statusLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -10),
            
            progressIndicator.topAnchor.constraint(equalTo: statusLabel.bottomAnchor, constant: 8),
            progressIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            
            expandButton.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -20),
            expandButton.centerXAnchor.constraint(equalTo: view.centerXAnchor)
        ])
    }
    
    func mascotDragEntered() {
        iconView.contentTintColor = NSColor.controlAccentColor
        statusLabel.stringValue = "Release to Convert"
        statusLabel.textColor = NSColor.controlAccentColor
    }
    
    func mascotDragExited() {
        iconView.contentTintColor = NSColor.secondaryLabelColor
        statusLabel.stringValue = "Drop file here"
        statusLabel.textColor = NSColor.secondaryLabelColor
    }
    
    func mascotDropPerformed(path: String) {
        iconView.contentTintColor = NSColor.secondaryLabelColor
        statusLabel.stringValue = "Converting..."
        statusLabel.textColor = NSColor.labelColor
        
        progressIndicator.isHidden = false
        progressIndicator.startAnimation(nil)
        expandButton.isEnabled = false
        
        APIClient.shared.convertFile(path: path) { [weak self] success in
            DispatchQueue.main.async {
                self?.progressIndicator.stopAnimation(nil)
                self?.progressIndicator.isHidden = true
                self?.expandButton.isEnabled = true
                
                if success {
                    self?.iconView.contentTintColor = NSColor.systemGreen
                    self?.statusLabel.stringValue = "Converted successfully!"
                    self?.statusLabel.textColor = NSColor.systemGreen
                } else {
                    self?.iconView.contentTintColor = NSColor.systemRed
                    self?.statusLabel.stringValue = "Conversion failed"
                    self?.statusLabel.textColor = NSColor.systemRed
                }
                
                // Reset status after 3.5 seconds
                DispatchQueue.main.asyncAfter(deadline: .now() + 3.5) {
                    self?.iconView.contentTintColor = NSColor.secondaryLabelColor
                    self?.statusLabel.stringValue = "Drop file here"
                    self?.statusLabel.textColor = NSColor.secondaryLabelColor
                }
            }
        }
    }
    
    @objc func expandToDashboard() {
        guard let window = self.view.window else { return }
        
        // Keka-style CoreAnimation window resizing
        let newSize = NSSize(width: 960, height: 620)
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
            let dashboard = DashboardController()
            window.contentViewController = dashboard
        }
    }
}

// Custom view to handle dragging (Keka style)
class DropZoneView: NSView {
    weak var controller: DropZoneController?
    
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        registerForDraggedTypes([.fileURL])
        wantsLayer = true
        layer?.cornerRadius = 16
        layer?.backgroundColor = NSColor.clear.cgColor
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func draggingEntered(_ sender: NSDraggingInfo) -> NSDragOperation {
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.2
            self.layer?.backgroundColor = NSColor.selectedControlColor.withAlphaComponent(0.15).cgColor
        }
        controller?.mascotDragEntered()
        return .copy
    }

    
    override func draggingExited(_ sender: NSDraggingInfo?) {
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.2
            self.layer?.backgroundColor = NSColor.clear.cgColor
        }
        controller?.mascotDragExited()
    }
    
    override func performDragOperation(_ sender: NSDraggingInfo) -> Bool {
        draggingExited(nil)
        
        guard let urls = sender.draggingPasteboard.readObjects(forClasses: [NSURL.self], options: nil) as? [URL],
              let url = urls.first else { return false }
        
        controller?.mascotDropPerformed(path: url.path)
        return true
    }
}
