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
    rustup component add rust-std llvm-tools-preview cargo rust-src || fatal "Components installation failed! Abort"
    cargo install bootimage || fatal "Can't install bootimage! Abort"
}

# Call (May use additional arguments)
main