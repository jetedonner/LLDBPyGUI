// NO DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -framework Cocoa -o cocoa_windowed_objc2 cocoa_windowed_objc2.m -isysroot $(xcrun --show-sdk-path)
//
// WITH DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -g -framework Cocoa -o cocoa_windowed_objc2 cocoa_windowed_objc2.m -isysroot $(xcrun --show-sdk-path)
//
// Make executable:
// chmod u+x cocoa_windowed_objc2
//
// Codesign for MacOS
// codesign --verbose=4 --timestamp --strict --options runtime -s "<YOUR SIGNING CERTIFICATE NAME>" cocoa_windowed_objc2 --force

// Compile with: clang -target x86_64-apple-macos -arch x86_64 -g -framework Cocoa -o cocoa_windowed_objc2 cocoa_windowed_objc2.m -isysroot $(xcrun --show-sdk-path)
// A simple macOS GUI application using Objective-C++ and Cocoa for testing LLDBGUI (a python dbugger using lldbs python api).

#include <Cocoa/Cocoa.h>

@interface AppDelegate : NSObject <NSApplicationDelegate>
@property (strong) NSWindow *window;
@end

@implementation AppDelegate

// Action method for the button
- (void)showMessage:(id)sender {
    [self.window makeKeyAndOrderFront:nil];
    NSAlert *alert = [[NSAlert alloc] init];
    [alert setMessageText:@"Hello, Debugger!"];
    [alert addButtonWithTitle:@"OKely Dokely"];
    [alert runModal];
}

// - (void)askForUserName:(id)sender {
//     NSAlert *alert = [[NSAlert alloc] init];
//     [alert setMessageText:@"Enter your name"];
//     [alert setInformativeText:@"Please type your name below:"];
//     [alert addButtonWithTitle:@"OK"];
//     [alert addButtonWithTitle:@"Cancel"];
//
//     NSTextField *inputField = [[NSTextField alloc] initWithFrame:NSMakeRect(0, 0, 200, 24)];
// //     [inputField becomeFirstResponder]; // Ensure focus
// //     [alert setAccessoryView:inputField];
//
//     // Bring app to front
// //     [NSApp activateIgnoringOtherApps:YES];
//
//     NSModalResponse response = [alert runModal];
//     if (response == NSAlertFirstButtonReturn) {
//         NSString *name = [inputField stringValue];
//         NSLog(@"User entered name: %@", name);
//         // You can now use the name
//     }
// }

- (void)askForUserName:(id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    [alert setMessageText:@"What's your name?"];
    [alert setInformativeText:@"Please enter your name below:"];
    [alert addButtonWithTitle:@"OK"];
    [alert addButtonWithTitle:@"Cancel"];

    NSTextField *inputField = [[NSTextField alloc] initWithFrame:NSMakeRect(0, 0, 200, 24)];
    [inputField setEditable:YES];
    [inputField setBezeled:YES];
    [inputField setDrawsBackground:YES];
    [inputField setStringValue:@""]; // Optional default value

    [alert setAccessoryView:inputField];

    // Bring app and alert to front
    [NSApp activateIgnoringOtherApps:YES];
    [[alert window] makeKeyAndOrderFront:nil];
    [inputField becomeFirstResponder];

    NSModalResponse response = [alert runModal];
    if (response == NSAlertFirstButtonReturn) {
        NSString *name = [inputField stringValue];
        NSLog(@"User entered name: %@", name);
        // You can now use the name, e.g., update a label or store it
    }
}


- (void)applicationDidFinishLaunching:(NSNotification *)notification {
//     self.askForUserName()
    // Create the window
    NSRect frame = NSMakeRect(0, 0, 400, 200);
    self.window = [[NSWindow alloc] initWithContentRect:frame
                                              styleMask:(NSWindowStyleMaskTitled |
                                                         NSWindowStyleMaskClosable |
                                                         NSWindowStyleMaskMiniaturizable)
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    [self.window setTitle:@"Hello World App for debugger tests"];

    // Create a text field
    NSTextField *label = [[NSTextField alloc] initWithFrame:NSMakeRect(100, 80, 200, 40)];
    [label setStringValue:@"Hello, Debugger!"];
    [label setBezeled:NO];
    [label setDrawsBackground:NO];
    [label setEditable:NO];
    [label setSelectable:NO];
    [label setAlignment:NSTextAlignmentCenter];
    [label setFont:[NSFont systemFontOfSize:24]];

    [[self.window contentView] addSubview:label];

    NSButton *leftButton = [[NSButton alloc] initWithFrame:NSMakeRect(100, 140, 80, 30)];
    [leftButton setTitle: @"InputBox"];
    [leftButton setTarget:self];
    [leftButton setAction:@selector(askForUserName:)];
    [[self.window contentView] addSubview:leftButton];

    NSButton *rightButton = [[NSButton alloc] initWithFrame:NSMakeRect(200, 140, 80, 30)];
    [rightButton setTitle: @"AlertBox"];
    [rightButton setTarget:self];
    [rightButton setAction:@selector(showMessage:)];
    [[self.window contentView] addSubview:rightButton];
    [self.window makeKeyAndOrderFront:nil];
}

- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    return YES;
}
@end

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        // Create the application
        NSApplication *app = [NSApplication sharedApplication];

        // Set the delegate
        AppDelegate *delegate = [[AppDelegate alloc] init];
        [app setDelegate:delegate];

        // Run the application
        [app run];
    }
    return 0;
}
