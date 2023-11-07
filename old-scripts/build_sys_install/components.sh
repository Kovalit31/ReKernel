#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    + "Components can't be installed, abort!" rustup component add rust-std llvm-tools-preview cargo rust-src
    + "Bootimage (for legacy) can't be intalled, abort!" cargo install bootimage
}

# Call (May use additional arguments)
main