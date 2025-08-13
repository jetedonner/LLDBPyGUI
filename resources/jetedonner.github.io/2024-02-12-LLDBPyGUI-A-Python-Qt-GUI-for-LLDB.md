---
layout: post
title:  "LLDBPyGUI - GUI for LLDB Debugger Python API with PyQt6"
author: dave
date:   2025-07-16 13:06:53 +0200
categories: [Debugger, LLDB]
tags: [Debugger, LLDB, PyQt6]
published: false 
---
# LLDBPyGUI

 - VERSION: 0.0.2 - "Developer Preview" as of 2025-07-16 13:20:59

![LLDBPyGUI](../../assets/img/projects/lldbpygui/LLDBPyGUI-v0.0.2-2025-07-16-Teaser-Main-View-01_1920x1149-01.png)

    
## Old version
![LLDBPyGUI](../../assets/img/projects/lldbpygui/LLDBPyGUI-MainView-2024-02-28.png)

## Synopsis
LLDBPyGUI is a longtime missed gui of mine for the opensource debugger (framework) LLDB. While LLDB comes with a comperhensive set of tools and also a C++ and Python API. It lacks of providing a useful (at least for me) GUI as it's only working as a terminal application at this day of age. So I took some time and started a GUI wrapper project that is using the Python API of LLDB and began to implement a UI with the help of PyQt6. The project is still in a really early prototype stage at the moment, but I didn't want to let you miss the idea of mine and give you a short sneak-preview of the tool I have in mind.

## Movie Trailer
<div class="container-responsive-iframe">
<iframe class="responsive-iframe" src="https://www.youtube.com/embed/WGJYLz1r118" title="Python GUI for the LLDB Debugger Python API" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

## Features
- General info about the target executable and linked libraries 
- Disassembler / Debugger
- Stacktrace viewer
- Break- and Watchpoints
- Register / Variable viewer
- Synchronized source code view
- Memory viewer
- Search function
- Commands interface (for lldb cmds)

## Requirements (Important) 
The following requirements are strictly needed. You might get the python scripts to load in earlier lldb / clang versions, but you are strictly advised to use at least version 22.0.0git because of the buggy nature of older LLDB Python API versions. Test it at your own risk and expense, no support or help will be provided for setting LLDBPyGUI up in older LLDB / LLVM versions.

### macOS 
- macOS Sequoia >= 15.1.1 - At the moment LLDBPyGUI is soly developed and tested on macOS 15.1.1. You are encouraged to test it on other os versions or systems -at your own risk and expense of course. Every seriouse feedback is very welcome and will be noticed and processed personally by meyself.

### LLDB Python API base
- lldb version 22.0.0git
- clang version 22.0.0git

## Setup / Installation
### Compile LLDB (LLVM)
To use LLDBPyGUI you need to have *lldb* and *clang* installed and working with python scripting option enabled. Usually the preinstalled versions (~=16.0.0) of this appss are outdated and will lead to many headaches and problems while using all the features of LLDBPyGUI to debug executables or libraries. So the current version of LLDBPyGUI is tailored only for LLDB v. 22.0.0git and above, troubles with other versions are your own problem and will not be supported.

*Setup include path (i.e. add to ~/.zshrc or ~/.bashrc)*
```bash
dave@Aeon ~ % export SDKROOT=$(xcrun --show-sdk-path)
```

*Configure cmake*
```bash
dave@Aeon ~ % cmake -S llvm -B build -G Ninja -DLLVM_ENABLE_PROJECTS="clang;lldb" -DCMAKE_BUILD_TYPE=Release -DLLDB_INCLUDE_TESTS=OFF -DLLDB_ENABLE_PYTHON=ON -DPython3_ROOT_DIR=/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9
```

*Build with cmake*
```bash
dave@Aeon ~ % cmake --build build
```

```bash
dave@Aeon ~ % lldb --version 
lldb version 22.0.0git (https://github.com/llvm/llvm-project.git revision 16a0892a9db1825ffa5e42b801e13215418d93b9)
  clang revision 16a0892a9db1825ffa5e42b801e13215418d93b9
  llvm revision 16a0892a9db1825ffa5e42b801e13215418d93b9
```
 
## How to install and run the app
To install the LLDBPyGUI app to LLDB you have to amend the .lldbinit file in you users home directory like so:

```bash
command script import /<pathToGuiScripts>/lldbpyGUI.py
```
(~/.lldbinit file)

To run the python app start a lldb instance with
```bash
dave@Aeon ~ % lldb
(LLDBPyGUI) pyg
#=================================================================================#
| Starting TEST ENVIRONMENT for LLDBPyGUI (ver. 0.0.2 - DEV PREVIEW)              |
|                                                                                 |
| Desc:                                                                           |
| This python script is for development and testing while development             |
| of the LLDB python GUI (LLDBPyGUI.py) - use at own risk! No Warranty!           |
|                                                                                 |
| Credits:                                                                        |
| - LLDB                                                                          |
| - lldbutil.py                                                                   |
| - lui.py                                                                        |
|                                                                                 |
| Author / Copyright:                                                             |
| Kim David Hauser (JeTeDonner), (C.) by kimhauser.ch 1991-2025                   |
#=================================================================================#
```

*Old Version*
```bash
dave@Aeon ~ % lldb
[+] Loaded LLDBPyGUI version 0.0.1 - ALPHA PREVIEW (BUILD: 689)
(LLDBPyGUI) spg
```

## Features

### Shortcuts (mouse and keyboard)
#### Shift click to copy
You can almost 'shift+click' any gui element to copy it text value to clipboard. This can become very handy at some times :-)



### Helpers
#### Texts / TreeView / TableView => Shift+Click: Copy text to Clipboard
If you do any "Shift+Click" on a Text-/Edit-Field, TreeView or TableView the text under the cursor will be copied to clipboard for further use. You can enable/disable this function in the settings.

#### Console: Save Commands History
The commands you enter to the consoles in LLDBPyGUI can be saved to a history file so you can go back or "scroll" through the commands you already entered. You can enable/disable this function in the settings.

### Community contribution
As you can see this project is still under construction and not finished yet. So far I did what I could and what I thought was useful and would be needed. But let's face it, the product is not final yet and every help or contribution is very welcome. If you think this tool is useful for you but is missing some important function you need, please don't hesitate to contact me personally or even better send me any pull request via github. I really think this project is worth a glimp and could help many developers. Please keep in mind, that at this stage you have to meet several really specific conditions which are crucial for running this early Developer Preview of LLDBPyGUI.

### Disclaimer
Please keep in mind, that this release is only a really early Alpha release version that is intend to give you a first preview of what the app will look and function like. There is no waranty or garantie of working functionality or working feature what so ever. Anyhow every feedback or input from your side is very welcome as this will give me an idea what is important to you as an end user. So please feel free to send me any feedback about the app and your opinion. Thank you!

## Documentation

## Download / Github
- [Source code at GitHub](https://github.com/jetedonner/LLDBPyGUI)
<!-- - Zip file from mirror -->

## <a id="credits"></a>Credits
- [developer.arm.com](https://developer.arm.com/documentation){:target="_blank" rel="noopener"}
- [Mach-O Wikipedia](https://en.wikipedia.org/wiki/Mach-O){:target="_blank" rel="noopener"}

### LLDB
- [LLDB](https://lldb.llvm.org/){:target="_blank" rel="noopener"}

### Python libs
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt){:target="_blank" rel="noopener"}
- [ansi2html](https://github.com/pycontribs/ansi2html){:target="_blank" rel="noopener"}

### Images and Icons
- <a href="https://www.flaticon.com/free-icons/debug" title="debug icons">Debug icons created by Freepik - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/video-player" title="video player icons">Video player icons created by judanna - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/github" title="github icons">Github icons created by Pixel perfect - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/triangle" title="triangle icons">Triangle icons created by Freepik - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/pause" title="pause icons">Pause icons created by Freepik - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/settings" title="settings icons">Settings icons created by Gregor Cresnar Premium - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/info" title="info icons">Info icons created by Plastic Donut - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/save" title="save icons">Save icons created by Flat Icons - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/edit" title="edit icons">Edit icons created by Flat Icons - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/recycle-bin" title="recycle bin icons">Recycle bin icons created by Uniconlabs - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/settings" title="settings icons">Settings icons created by Md Tanvirul Haque - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/settings" title="settings icons">Settings icons created by Freepik - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/reload" title="reload icons">Reload icons created by syafii5758 - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/add" title="add icons">Add icons created by Ilham Fitrotul Hayat - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/ui" title="ui icons">Ui icons created by khulqi Rosyid - Flaticon</a>
