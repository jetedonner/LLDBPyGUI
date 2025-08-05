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

#include <objc/runtime.h>
#include <objc/message.h>
#include <CoreGraphics/CoreGraphics.h>

#define cls objc_getClass
#define sel sel_getUid
#define msg ((id (*)(id, SEL, ...))objc_msgSend)
#define cls_msg ((id (*)(Class, SEL, ...))objc_msgSend)

int main(int argc, char *argv[]) {
    id app = cls_msg(cls("NSApplication"), sel("sharedApplication"));
    msg(app, sel("setActivationPolicy:"), 0); // NSApplicationActivationPolicyRegular

    CGRect frame = CGRectMake(0, 0, 600, 400);
    id window = msg(cls_msg(cls("NSWindow"), sel("alloc")),
                    sel("initWithContentRect:styleMask:backing:defer:"),
                    frame,
                    0x0, // 0x0B,  //`(1 << 3), // NSWindow.StyleMask.resizable/*(1 << 0) | (1 << 1) | (1 << 3)*/, // Titled | Closable | Resizable, // Titled | Closable | Resizable
                    2, // NSBackingStoreBuffered
                    NO);

    id title = cls_msg(cls("NSString"), sel("stringWithUTF8String:"), "Pure C Window");
    msg(window, sel("setTitle:"), title);
    msg(window, sel("makeKeyAndOrderFront:"), nil);
    msg(app, sel("activateIgnoringOtherApps:"), YES);
    msg(app, sel("run"));

    return 0;
}
