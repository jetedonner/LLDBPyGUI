//
//  ViewController.swift
//  SwiftREPLTestApp
//
//  Created by Kim David Hauser on 05.08.2025.
//

import Cocoa

class ViewController: NSViewController {

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

