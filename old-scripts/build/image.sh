#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    cd "$BASEDIR/build"
    if [ "$1" == "debug" ]; then
        if [ -d "image" ]; then
            cd image/
            + "Image build failed!" cargo build
            exit 0
        fi
        cd kernel/
        + "Bootimage create failed!" cargo bootimage
    else
        if [ -d "image" ]; then
            cd image/
            + "Image build failed!" cargo build --release
            exit 0
        fi
        cd kernel/
        + "Bootimage create failed!" cargo bootimage --release
    fi
}

# Call (May use additional arguments)
main "$4"