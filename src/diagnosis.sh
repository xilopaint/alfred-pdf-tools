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
echo '### macOS version'
/usr/bin/sw_vers -productVersion

echo
echo '### Architecture'
/usr/bin/arch
echo