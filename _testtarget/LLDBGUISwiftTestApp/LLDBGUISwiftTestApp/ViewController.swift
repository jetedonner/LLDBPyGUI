//
//  ViewController.swift
//  LLDBGUISwiftTestApp
//
//  Created by Kim David Hauser on 28.09.2025.
//

import Cocoa

class ViewController: NSViewController {

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
}

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }

    @IBAction func testButtonAction(_ sender: Any?) {
        let alert = NSAlert()
        alert.messageText = "Hello"
        alert.addButton(withTitle: "OK")
        alert.alertStyle = .informational
        alert.runModal()
    }

}

