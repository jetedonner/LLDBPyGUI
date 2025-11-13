#import <Cocoa/Cocoa.h>

@interface AppDelegate : NSObject <NSApplicationDelegate>
@property (strong) NSWindow *window;
@end

@implementation AppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    // Create window
    NSRect frame = NSMakeRect(0, 0, 400, 200);
    self.window = [[NSWindow alloc] initWithContentRect:frame
                                              styleMask:(NSWindowStyleMaskTitled |
                                                         NSWindowStyleMaskClosable)
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    [self.window setTitle:@"Name Prompt App"];
    [self.window center];

    // Create button
    NSButton *button = [[NSButton alloc] initWithFrame:NSMakeRect(150, 80, 100, 40)];
    [button setTitle:@"Enter Name"];
    [button setTarget:self];
    [button setAction:@selector(promptForName:)];
    [[self.window contentView] addSubview:button];

    [self.window makeKeyAndOrderFront:nil];
}

- (void)promptForName:(id)sender {
    // Create alert with text field
    NSAlert *alert = [[NSAlert alloc] init];
    [alert setMessageText:@"What's your name?"];
    [alert addButtonWithTitle:@"OK"];
    [alert addButtonWithTitle:@"Cancel"];

    NSTextField *inputField = [[NSTextField alloc] initWithFrame:NSMakeRect(0, 0, 200, 24)];
    [inputField setPlaceholderString:@"Enter your name"];
    [alert setAccessoryView:inputField];

    // Show alert
    NSModalResponse response = [alert runModal];
    if (response == NSAlertFirstButtonReturn) {
        NSString *name = [inputField stringValue];
        if (name.length == 0) name = @"Stranger";

        // Show greeting
        NSAlert *greeting = [[NSAlert alloc] init];
        [greeting setMessageText:[NSString stringWithFormat:@"Hello, %@!", name]];
        [greeting addButtonWithTitle:@"Nice!"];
        [greeting runModal];
    }
}

- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    return YES;
}
@end

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSApplication *app = [NSApplication sharedApplication];
        AppDelegate *delegate = [[AppDelegate alloc] init];
        [app setDelegate:delegate];
        [app run];
    }
    return 0;
}
