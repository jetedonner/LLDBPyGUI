# LLDBPyGUI 
A python GUI for LLDB implemented with PyQt6. (This is a LLDB internal script with custom commands and a include version of lldbinit)

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

## Download / Github
- [Source code at GitHub](https://github.com/jetedonner/pyLLDBGUI)
<!-- - Zip file from mirror -->

## <a id="credits"></a>Credits
- [developer.arm.com](https://developer.arm.com/documentation){:target="_blank" rel="noopener"}
- [Mach-O Wikipedia](https://en.wikipedia.org/wiki/Mach-O){:target="_blank" rel="noopener"}