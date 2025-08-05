// NO DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -o amicable_numbers amicable_numbers.c -isysroot $(xcrun --show-sdk-path)
//
// WITH DEBUG-INFO:
// clang -g -target x86_64-apple-macos -arch x86_64 -o amicable_numbers amicable_numbers.c -isysroot $(xcrun --show-sdk-path)
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

#import <Cocoa/Cocoa.h> // Import the Cocoa framework for GUI elements.

// Define the application delegate class.
// This class handles application-level events, like launching and quitting.
@interface AppDelegate : NSObject <NSApplicationDelegate>
@end

@implementation AppDelegate

// This method is called when the application has finished launching.
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
    // Get the shared application instance.
    NSApplication *app = [NSApplication sharedApplication];

    // Create a new window.
    // NSWindow is the class for creating windows.
    // The arguments define its frame (position and size), style mask, backing store, and deferred creation.
    NSRect frame = NSMakeRect(100, 100, 400, 300); // x, y, width, height
    NSUInteger styleMask = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable | NSWindowStyleMaskMiniaturizable;
    NSWindow *window = [[NSWindow alloc] initWithContentRect:frame
                                                    styleMask:styleMask
                                                      backing:NSBackingStoreBuffered
                                                        defer:NO];

    // Set the window's title.
    [window setTitle:@"My Simple C++ GUI App"];

    // Set the window's content view.
    // A content view is where all other UI elements (buttons, labels, etc.) will be placed.
    // For a simple window, we can just use a generic NSView.
    NSView *contentView = [[NSView alloc] initWithFrame:[window contentRectForFrameRect:frame]];
    [window setContentView:contentView];

    // Create a simple text label.
    // NSTextField is used for displaying static text or editable text fields.
    NSRect labelFrame = NSMakeRect(50, 200, 300, 30); // Position within the content view
    NSTextField *label = [[NSTextField alloc] initWithFrame:labelFrame];
    [label setStringValue:@"Hello from C++ on macOS!"]; // Set the text
    [label setBezeled:NO]; // Remove border
    [label setDrawsBackground:NO]; // Make background transparent
    [label setEditable:NO]; // Make it non-editable
    [label setSelectable:NO]; // Make text non-selectable
    [label setAlignment:NSTextAlignmentCenter]; // Center the text

    // Add the label to the window's content view.
    [contentView addSubview:label];

    // Make the window visible and bring it to the front.
    [window makeKeyAndOrderFront:nil];

    // Activate the application. This is important for the app to receive events.
    [app activateIgnoringOtherApps:YES];

    // Release the window and content view if not using ARC, but with ARC (default for modern Xcode/Clang),
    // these are automatically managed. We keep references for clarity.
    // [window release]; // Not needed with ARC
    // [contentView release]; // Not needed with ARC
    // [label release]; // Not needed with ARC
}

// This method is called when the application is about to terminate.
- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    return YES; // Terminate the application when the last window is closed.
}

@end

// The main function, entry point of the application.
int main(int argc, const char * argv[]) {
    // Create an autorelease pool.
    // All objects created with `alloc` and `init` are put into this pool
    // and released when the pool is drained. Essential for Objective-C memory management.
    @autoreleasepool {
        // Create the NSApplication instance. This is the central object for a Cocoa application.
        NSApplication *app = [NSApplication sharedApplication];

        // Set the application delegate.
        // The delegate receives messages about application-level events.
        AppDelegate *delegate = [[AppDelegate alloc] init];
        [app setDelegate:delegate];

        // Run the application's event loop.
        // This starts processing events (mouse clicks, key presses, window events, etc.)
        // and keeps the application running until it's terminated.
        [app run];

        // Release the delegate if not using ARC.
        // [delegate release]; // Not needed with ARC
    }
    return 0; // Return 0 to indicate successful execution.
}
