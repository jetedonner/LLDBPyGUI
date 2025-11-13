// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// NG: clang -g -o hello_library_exec hello_library_exec.c -ldl -isysroot $(xcrun --show-sdk-path)
//     clang -g -o hello_library_exec hello_library_exec.c -ldl
//     clang -g -o hello_library_exec hello_library_exec.c -L. -lexternal -rpath @executable_path
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <dlfcn.h>  // For dynamic loading

void subfunc(int idx, int var) {
    printf("%d -> %d\n", idx, var);
    fflush(stdout);
}

int main() {
    int idx = 0;
    int testVar = 123;
    char hardcoded_string[] = "S3CR3T";

    printf("Hello test: %d / %s\n", testVar, hardcoded_string);
    fflush(stdout);

    // Load the dynamic library
    void *handle = dlopen("./libexternal.dylib", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "❌ Failed to load library: %s\n", dlerror());
        return 1;
    }

    // Get the function pointer
    void (*callExternalFunc)() = dlsym(handle, "callExternalFunc");
    if (!callExternalFunc) {
        fprintf(stderr, "❌ Failed to find symbol: %s\n", dlerror());
        dlclose(handle);
        return 1;
    }

    void (*callExternalFuncWithParam)(int param) = dlsym(handle, "callExternalFuncWithParam");
    if (!callExternalFuncWithParam) {
        fprintf(stderr, "❌ Failed to find symbol: %s\n", dlerror());
        dlclose(handle);
        return 1;
    }

    while (1) {
        if (idx % 3 == 0) {
            subfunc(idx, testVar);
        }
        if (idx % 6 == 0) {
            callExternalFunc();  // Call the function from the dylib
        }
        if (idx % 9 == 0) {
            callExternalFuncWithParam(idx);  // Call the function from the dylib
        }
        printf("...\n");
        fflush(stdout);
        sleep(1);
        idx++;
    }

    dlclose(handle);
    return 0;
}
