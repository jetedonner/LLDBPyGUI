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
// NG: clang -g -dynamiclib -o libexternal2.dylib hello_library_lib2.c -isysroot $(xcrun --show-sdk-path)
//     clang -g -dynamiclib -o libexternal2.dylib hello_library_lib2.c
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

// hello_library_lib2.c
#include <stdio.h>

void callExternalFunc2() {
    printf("HELLO From Library TWO - 222 TWOTWOTWO!!!\n");
    fflush(stdout);
}

void callExternalInternalFuncWithParam2(int param) {
    printf("HELLO From Library INTERNAL FUNCTION WITH PARAM: %d ... TWO - 222 TWOTWOTWO!!!\n", param);
    fflush(stdout);
}

void callExternalFuncWithParam2(int param) {
    printf("HELLO From Library WITH PARAM: %d ...  TWO - 222 TWOTWOTWO!!!\n", param);
    fflush(stdout);

    callExternalInternalFuncWithParam2(param * 2);
}