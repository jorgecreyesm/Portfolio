#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(which python3)"
PLIST="$HOME/Library/LaunchAgents/com.jorgereyeso.jobtracker.plist"

echo "Installing Job Application Tracker server..."

# Install dependencies
"$PYTHON" -m pip install -q flask flask-cors openpyxl

# Write the LaunchAgent plist with the correct paths
cat > "$PLIST" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jorgereyeso.jobtracker</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$SCRIPT_DIR/server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/jobtracker.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/jobtracker.error.log</string>
</dict>
</plist>
PLIST_EOF

# Unload existing instance if running, then load fresh
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo ""
echo "✓ Server installed and running on http://localhost:5050"
echo ""
echo "Now load the Chrome extension:"
echo "  1. Open Chrome → chrome://extensions"
echo "  2. Enable Developer mode (toggle, top right)"
echo "  3. Click 'Load unpacked'"
echo "  4. Select this folder: $SCRIPT_DIR/extension"
echo ""
echo "Done! Click the extension icon on any job posting to log it."
