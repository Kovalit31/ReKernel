#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

# Logger
log() {
    (echo -e "\n$1" | tee -a -i $LOGGER) > /dev/null
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
    if [ -d "$BASEDIR/build" ]; then
        rm -rf "$BASEDIR/build"
    fi
    if [ -d "$1" ]; then
        rm -rf "$1"
    fi
}

# Call (May use additional arguments)
main "$4"