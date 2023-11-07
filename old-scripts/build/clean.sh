#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    if [ -d "$BASEDIR/build" ]; then
        + "Can't clean build dir!" rm -rf "$BASEDIR/build"
    fi
    if [ -d "$1" ]; then
        + "Can't remove logs!" rm -rf "$1"
    fi
}

# Call (May use additional arguments)
main "$4"