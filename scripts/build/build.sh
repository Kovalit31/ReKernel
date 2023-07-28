#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    cd "$BASEDIR/build/kernel"
    if [ "$1" == "debug" ]; then
        + "Build failed!\nNote: May you need clean working directory?\nRun 'build.py clean'" cargo build
    else
        + "Build failed!\nNote: May you need clean working directory?\nRun 'build.py clean'" cargo build --release
    fi
}

# Call (May use additional arguments)
main "$4"