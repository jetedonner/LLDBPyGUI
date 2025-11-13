//
//  ViewController.swift
//  SwiftTestApp4LLDBGUI
//
//  Created by Kim-David Hauser on 11.10.2025.
//

import Cocoa

class ViewController: NSViewController {

    @IBOutlet weak var textField: NSTextField!
    
    override func viewDidLoad() {
        super.viewDidLoad()
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }

    @IBAction func buttonClicked(_ sender: Any) {
        print("Button clicked")
        let msg = NSAlert()
        msg.alertStyle = .critical
        msg.icon = NSImage(systemSymbolName: NSImage.computerName, accessibilityDescription: nil)
        msg.messageText = "Hello \(textField.stringValue) => Button clicked by you. Thanks ..."
        msg.runModal()
    }
}
