#!/bin/bash

echo '### Workflow version'
/usr/libexec/PlistBuddy -c 'Print :version' info.plist

echo
echo '### Alfred version'
/usr/bin/osascript -e 'tell application id "com.runningwithcrayons.Alfred" to return version'

echo
echo '### Python version'
python3 --version | awk '{print $NF}'

echo
echo '### PyCryptodome version'
output=$(python3 -c "import Crypto; print(Crypto.__version__)" 2>/dev/null)
if [[ -n $output ]]; then
    printf "%s\n" "$output"
else
    printf "Not Installed\n"
fi

echo
echo '### Rosetta installation status'
if [[ $(/usr/bin/pgrep oahd) ]]; then
    printf "Installed\n"
else
    printf "Not Installed\n"
fi

echo
echo '### macOS version'
/usr/bin/sw_vers -productVersion

echo
echo '### Architecture'
/usr/bin/arch
echo
