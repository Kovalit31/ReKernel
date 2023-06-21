#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"


# Logger
log() {
    (echo "$1" | tee -a -i $LOGGER) > /dev/null
}

# Fatal trap. CAUTION: Kills parrent and stop executing!
fatal() {
    log "$1"
    kill -SIGTERM $PARENT_PID
    exit 1
}

# Lifecycle
main() {
    cd "$BASEDIR/build"
    if [ "$1" == "debug" ]; then
        cargo build
        if [ ! -d "kernel" ]; then
            cargo bootimage
        fi
    else
        cargo build --release
        if [ ! -d "kernel" ]; then
            cargo bootimage --release
        fi
    fi
}

# Call (May use additional arguments)
main "$4"