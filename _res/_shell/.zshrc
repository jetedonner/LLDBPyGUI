# PYTHONPATH is an environment variable that is used to 
# specify the location of Python libraries. It is typic-
# ally used by developers to ensure that their code can
# find the required Python libraries.
PYTHONPATH="/opt/homebrew/bin"
alias python3="/opt/homebrew/bin/python3.9"
export PATH="$HOME/.composer/vendor/bin:$PATH"
export ANDROID_HOME='/Users/dave/Library/Android/sdk/'
export ANDROID_SDK_ROOT='/Users/dave/Library/Android/sdk/'
export ANDROID_AVD_HOME=~/.android/avd

export PATH="/opt/homebrew/opt/chruby/share/chruby:$PATH"
source /opt/homebrew/opt/chruby/share/chruby/chruby.sh
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

function findng() {
    find "$1" -name "$2" -print 2>/dev/null
}

function findng2() {
    echo "Trying to find $2 recursively in $1 ..."
    find "$1" -type f -exec grep -l "$2" {} +
    #find "$1" -name "*$2*" -print 2>/dev/null
}



#scp -r /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk root@Patty:/var/jb/var/root/dev/_res/sdks

# Herd injected PHP 8.3 configuration.
# export HERD_PHP_83_INI_SCAN_DIR="/Users/dave/Library/Application Support/Herd/config/php/83/"


# Herd injected NVM configuration
# export NVM_DIR="/Users/dave/Library/Application Support/Herd/config/nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
# 
# [[ -f "/Applications/Herd.app/Contents/Resources/config/shell/zshrc.zsh" ]] && builtin source "/Applications/Herd.app/Contents/Resources/config/shell/zshrc.zsh"

# Herd injected PHP binary.
# export PATH="/Users/dave/Library/Application Support/Herd/bin/":$PATH
export PATH="/opt/homebrew/opt/libxml2/bin:$PATH"
export PATH="/usr/local/opt/libxml2/bin:$PATH"
export PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:$PATH"
#export THEOS="/Volumes/Data/dev/reversing/iOS/_iosappz/theos"
#export THEOS="/Volumes/Data/dev/reversing/iOS/_res/theos"
export THEOS="/Users/dave/theos"
export PATH="/Volumes/Data/dev/_res/appz/lldb/llvm-project/build/bin:/opt/homebrew/Cellar/ruby/3.4.4/bin:$THEOS:$THEOS/bin:$PATH"

autoload -Uz compinit
compinit
source /Users/dave/.pymobiledevice3.zsh

lldbclear() {
    lldb "$@"
    clear
    clear
}

lldbpyg() {
    lldb --one-line-before-file pyg
    clear
    clear
}

