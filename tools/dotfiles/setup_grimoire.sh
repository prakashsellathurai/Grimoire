#!/bin/bash
set -euo pipefail

GRIMOIRE_DIR="${GRIMOIRE_DIR:-$HOME/grimoire}"
GRIMOIRE_URL="https://github.com/prakashsellathurai/grimoire"
SHELL_INIT="$HOME/.bashrc"

if [ ! -d "$GRIMOIRE_DIR" ]; then
    echo "Cloning grimoire into $GRIMOIRE_DIR..."
    git clone "$GRIMOIRE_URL" "$GRIMOIRE_DIR"
else
    echo "grimoire already exists at $GRIMOIRE_DIR"
fi

TOOLS_DIR="$GRIMOIRE_DIR/tools/dotfiles"

# Make scripts executable
chmod +x "$TOOLS_DIR"/*.sh 2>/dev/null || true

PATH_CONTENT=$(cat <<EOF
# Grimoire scripts - add to PATH
export PATH="\$PATH:$TOOLS_DIR"
EOF
)

if grep -q "Grimoire scripts" "$SHELL_INIT" 2>/dev/null; then
    echo "grimoire PATH already configured in $SHELL_INIT"
else
    echo "" >> "$SHELL_INIT"
    echo "$PATH_CONTENT" >> "$SHELL_INIT"
    echo "Added grimoire to PATH in $SHELL_INIT"
fi

echo ""
echo "Setup complete! Run 'source $SHELL_INIT' or open a new shell."
echo "You can now call scripts directly: kill-port.sh 8080, add_journal_entry.sh 'my entry', etc."
