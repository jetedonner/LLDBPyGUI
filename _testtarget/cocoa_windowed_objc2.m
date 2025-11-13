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

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
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

    NSButton *rightButton = [[NSButton alloc] initWithFrame:NSMakeRect(100, 140, 200, 30)];
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
