#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

# Logger
log() {
    ( echo -e "\n$1" | tee -a -i $LOGGER ) > /dev/null
}

exec_log() {
    $@ > >( tee -a -i "$LOGGER" ) 2>&1
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
        exec_log cargo build
        if [ ! -d "kernel" ]; then
            exec_log cargo bootimage
        fi
    else
        exec_log cargo build --release
        if [ ! -d "kernel" ]; then
            exec_log cargo bootimage --release
        fi
    fi
}

# Call (May use additional arguments)
main "$4"