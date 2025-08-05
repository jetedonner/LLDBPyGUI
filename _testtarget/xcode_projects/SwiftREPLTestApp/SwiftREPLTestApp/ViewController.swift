//
//  ViewController.swift
//  SwiftREPLTestApp
//
//  Created by Kim David Hauser on 05.08.2025.
//

import Cocoa

class ViewController: NSViewController {

    @IBOutlet var textField:NSTextField?
    
    @IBAction func showMessageBox2(_ sender: Any) {
        let alert = NSAlert()
        if textField == nil || textField?.stringValue.isEmpty ?? true {
            alert.messageText = "Hello anonymous user"
            alert.informativeText = "Dear anonymous user enter your name for testing!"
            alert.alertStyle = .warning
        } else{
            alert.messageText = "Hello " + textField!.stringValue
            alert.informativeText = "Dear " + textField!.stringValue + " thank you for testing!"
            alert.alertStyle = .informational
        }
        
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }
    
    @IBAction func showMessageBox(_ sender: Any) {
        let alert = NSAlert()
        alert.messageText = "Hello"
        alert.informativeText = "This is a message box in a macOS App"
        alert.alertStyle = .informational
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }

    @IBAction func closeAppButtonTapped(_ sender: NSButton) {
        exit(0)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }


}

