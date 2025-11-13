# LLDBGUI: A Python GUI Extension for LLDB

## Introduction

LLDBGUI is a Python-based graphical interface for the LLDB debugger, built with PyQt6 and designed specifically for
macOS. It serves as an internal LLDB script that enhances the debugging experience by providing a visual layer on top of
LLDB’s powerful command-line capabilities. LLDBGUI includes custom debugger commands and ships with an integrated
version of lldbinit, allowing for seamless configuration and extended functionality out of the box.

This tool is ideal for developers who prefer a more intuitive, interactive approach to debugging, while still leveraging
the full depth of LLDB’s features. Whether you're inspecting variables, managing breakpoints, or navigating complex call
stacks, LLDBGUI streamlines the process with a responsive and user-friendly interface.
<!--
LLDBGUI is a python GUI for LLDB - implemented with PyQt6. (This is a LLDB internal script with custom commands and a included version of lldbinit)
-->
<!--
## Mainview
![Mainview](img/2025-08-29-01-TipsAndTricks-01-Main-GUI-Overview.png)

Compile custom LLDB and CLANG for use with LLDBPyGUI
```bash
cmake -S llvm -B build -G Ninja -DLLVM_ENABLE_PROJECTS="clang;lldb" -DCMAKE_BUILD_TYPE=Release -DLLDB_INCLUDE_TESTS=OFF -DLLDB_ENABLE_PYTHON=ON -DPython3_ROOT_DIR=/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9
```
Compile source code with custom CLANG
```bash
clang -g -target x86_64-apple-macos -arch x86_64 -o a_hello_world_test a_hello_world_test.c -isysroot $(xcrun --show-sdk-path)
```

## Synopsis
LLDBPyGUI is a longtime missed GUI of mine for the open source debugger (framework) LLDB. While LLDB comes with a comprehensive set of tools and also a C++ and Python API. It lacks of providing a useful (at least for me) GUI as it's only working as a terminal application at the present time. So I took some time and started a Python GUI wrapper project that is using the Python API of LLDB and began to implement a UI with the help of PyQt6. The project is still in a really early prototype stage at the moment, but I didn't want to let you miss the idea of mine and give you a short sneak-preview of the tool I have in mind.

## Movie Trailer
[![Youtube trailer](https://img.youtube.com/vi/WGJYLz1r118/hqdefault.jpg)](https://www.youtube.com/watch?v=WGJYLz1r118)

## Features
- General info about the target
- Disassembler / Debugger
- Stacktrace viewer
- Break- and Watchpoints
- Register / Variable viewer
- Synchronized source code
- Memory viewer
- Search function
- Commands interface

## Documentation
### Shortcuts and Tricks
#### Copy texts to clipboard - Shift + Click
Almost all texts in any view or widget can be copied to clipboard with shift + click on it.

## Download / Github
- [Source code at GitHub](https://github.com/jetedonner/pyLLDBGUI)-->
<!-- - Zip file from mirror -->
<!--
## <a id="credits"></a>Credits
- [developer.arm.com](https://developer.arm.com/documentation){:target="_blank" rel="noopener"}
- [Mach-O Wikipedia](https://en.wikipedia.org/wiki/Mach-O){:target="_blank" rel="noopener"}
-->