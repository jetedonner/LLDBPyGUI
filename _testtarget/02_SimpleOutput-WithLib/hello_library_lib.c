// NO DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -o a_hello_world_test a_hello_world_test.c -isysroot $(xcrun --show-sdk-path)
//
// WITH DEBUG-INFO:
// clang -g -target x86_64-apple-macos -arch x86_64 -o a_hello_world_test a_hello_world_test.c
// clang -g -target x86_64-apple-macos -arch x86_64 -o a_hello_world_test a_hello_world_test.c -isysroot $(xcrun --show-sdk-path)
//
// Make executable:
// chmod u+x hello_world
//
// Codesign for MacOS
// codesign --verbose=4 --timestamp --strict --options runtime -s "<YOUR SIGNING CERTIFICATE NAME>" hello_world --force


// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// NG: clang -g -dynamiclib -o libexternal.dylib hello_library_lib.c -isysroot $(xcrun --show-sdk-path)
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

// external_lib.c
#include <stdio.h>

void callExternalFunc() {
    printf("HELLO From Library!!!\n");
    fflush(stdout);
}
