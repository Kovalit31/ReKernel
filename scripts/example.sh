#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

# Logger
log() {
    (echo -e "\n$1" | tee -a -i $LOGGER) > /dev/null
}

exec_log() {
    ( ${@:2} || fatal "$1" ) > >( tee -a -i "$LOGGER" ) 2>&1
}

# Fatal trap. CAUTION: Kills parrent and stop executing!
fatal() {
    log "$1"
    kill -SIGTERM $PARENT_PID
    exit 1
}

# Lifecycle
main() {
    exec_log "It can't be raised! ._." echo "Hello world!"
}

# Call (May use additional arguments)
main