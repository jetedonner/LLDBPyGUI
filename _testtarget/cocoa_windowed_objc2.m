// NO DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -o cocoa_windowed_objc2 cocoa_windowed_objc2.m
//
// WITH DEBUG-INFO:
// clang -g -target x86_64-apple-macos -arch x86_64 -o cocoa_windowed_objc2 cocoa_windowed_objc2.m
//
// Make executable:
// chmod u+x amicable_numbers
//
// Codesign for MacOS
// codesign --verbose=4 --timestamp --strict --options runtime -s "<YOUR SIGNING CERTIFICATE NAME>" amicable_numbers --force

// Compile with: clang -framework Cocoa -o myapp myapp.c
// main.mm
// A simple macOS GUI application using Objective-C++ and Cocoa.
// This file must be compiled as Objective-C++ (e.g., with a .mm extension).


// hello_world.cpp
#include <Cocoa/Cocoa.h>

// Application Delegate
@interface AppDelegate : NSObject <NSApplicationDelegate>
@property (strong) NSWindow *window;
@end

@implementation AppDelegate

// Action method for the button
- (void)showMessage:(id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    [alert setMessageText:@"Hello, World!"];
    [alert addButtonWithTitle:@"OK"];
    [alert runModal];
}

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    // Create the window
    NSRect frame = NSMakeRect(0, 0, 400, 200);
    self.window = [[NSWindow alloc] initWithContentRect:frame
                                              styleMask:(NSWindowStyleMaskTitled |
                                                         NSWindowStyleMaskClosable |
                                                         NSWindowStyleMaskMiniaturizable)
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    [self.window setTitle:@"Hello World App"];

    // Create a text field
    NSTextField *label = [[NSTextField alloc] initWithFrame:NSMakeRect(100, 80, 200, 40)];
    [label setStringValue:@"Hello, World!"];
    [label setBezeled:NO];
    [label setDrawsBackground:NO];
    [label setEditable:NO];
    [label setSelectable:NO];
    [label setAlignment:NSTextAlignmentCenter];
    [label setFont:[NSFont systemFontOfSize:24]];

    // Add the label to the window's content view
    [[self.window contentView] addSubview:label];

    NSButton *rightButton = [[NSButton alloc] initWithFrame:NSMakeRect(100, 140, 200, 30)];
//     [rightButton setTarget:self];
//     [[rightButton cell] setHighlightsBy:NSNullCellType];
//     [rightButton setImage:[NSImage imageNamed:@"rightButton"]];
//     [rightButton setAction:@selector(action:)];
//     [rightButton setBordered:YES];
    [rightButton setTarget:self];
    [rightButton setAction:@selector(showMessage:)];
    [[self.window contentView] addSubview:rightButton];
    [self.window makeKeyAndOrderFront:nil];
}

// This method is called when the application is about to terminate.
- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    return YES; // Terminate the application when the last window is closed.
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
