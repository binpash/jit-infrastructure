#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"
PASH_TOP=${PASH_TOP:-$(git rev-parse --show-toplevel)}

cd $PASH_TOP

LOG_DIR=$PASH_TOP/install_logs
mkdir -p $LOG_DIR
PYTHON_PKG_DIR=$PASH_TOP/python_pkgs

# Check if venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo "Error: python3-venv module not found. Please install it:" >&2
    echo "  Ubuntu/Debian: sudo apt install python3-venv" >&2
    echo "  Fedora/RHEL: sudo dnf install python3" >&2
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv $PYTHON_PKG_DIR

# Install dependencies directly using venv's pip
echo "Installing Python dependencies..."
$PYTHON_PKG_DIR/bin/pip install --upgrade pip
$PYTHON_PKG_DIR/bin/pip install -r "$PASH_TOP/requirements.txt"

echo "Building runtime tools..."
cd "$PASH_TOP/runtime/"
case "$distro" in
    freebsd*) 
        gmake
        ;;
    *)
        make
        ;;
esac

echo " * * * "
echo "Installation complete!"
echo "To use sh-instrument.sh, export PASH_TOP: \`export PASH_TOP=$PASH_TOP\`"
echo " * * * "

