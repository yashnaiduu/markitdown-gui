import AppKit

class AppDelegate: NSObject, NSApplicationDelegate {
    var mainWindow: NSWindow!
    var backendProcess: Process?

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        startBackend()
        
        // Setup Keka-style floating drop-zone window
        let windowSize = NSSize(width: 250, height: 250)
        let windowRect = NSRect(x: 0, y: 0, width: windowSize.width, height: windowSize.height)
        
        mainWindow = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .miniaturizable, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        mainWindow.center()
        mainWindow.titleVisibility = .hidden
        mainWindow.titlebarAppearsTransparent = true
        mainWindow.isMovableByWindowBackground = true
        mainWindow.backgroundColor = NSColor.windowBackgroundColor
        
        // Load the view controller
        let viewController = DropZoneController()
        mainWindow.contentViewController = viewController
        
        mainWindow.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Kill the Python backend when the app closes
        backendProcess?.terminate()
    }
    
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }

    private func startBackend() {
        print("Starting Python Backend...")
        
        // For development, we run the Python backend from the parent directory's .venv
        // In a real release bundle, this path would point inside the App bundle's Resources folder
        let backendPath = "/Users/yashnaidu/Proj/markdownproj/server.py"
        let pythonExecutable = "/Users/yashnaidu/Proj/markdownproj/.venv/bin/python3"
        
        let task = Process()
        task.executableURL = URL(fileURLWithPath: pythonExecutable)
        task.arguments = [backendPath]
        
        do {
            try task.run()
            backendProcess = task
            print("Python Backend started successfully.")
        } catch {
            print("Failed to start Python backend: \(error)")
        }
    }
}
