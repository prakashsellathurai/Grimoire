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
AUTO_COMPLETE_CONTENT=$(cat <<'EOF'
# grimoire auto-complete
GRIMOIRE_DIR="$HOME/grimoire"
FOO_DIR="$GRIMOIRE_DIR/tools/dotfiles"

_trigger_compgen_filenames() {
    local cur="$1"
    grep -v -F -f <(compgen -d -P ^ -S '$' -- $FOO_DIR"$cur") \
        <(compgen -f -P ^ -S '$' -- $FOO_DIR"$cur") |
        sed -e 's|^\^'$FOO_DIR'||' -e 's/\$$/ /'
    compgen -d -S / -- $FOO_DIR"$cur" | sed -e 's|'$FOO_DIR'||'
}
run() {
    echo "Running: $@"
    bash "$FOO_DIR/$1" "${@:2}"
}
_trigger_complete() {
    local cur=${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=( $(_trigger_compgen_filenames "$cur") )
}
complete -o nospace -F _trigger_complete run
EOF
)

if grep -q "grimoire auto-complete" "$SHELL_INIT" 2>/dev/null; then
    echo "auto-complete already sourced in $SHELL_INIT"
else
    echo "" >> "$SHELL_INIT"
    echo "$AUTO_COMPLETE_CONTENT" >> "$SHELL_INIT"
    echo "Added grimoire auto-complete to $SHELL_INIT"
fi

echo ""
echo "Setup complete! Run 'source $SHELL_INIT' or open a new shell."
echo "Then use 'run <script_name>' to execute scripts in $TOOLS_DIR"
EOF
