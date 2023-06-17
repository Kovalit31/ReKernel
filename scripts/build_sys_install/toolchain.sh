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
    if [ "$1" = "x86_64" ]; then
        rustup toolchain install nightly-x86_64-unknown-linux-gnu || fatal "Toolchain not installable. Abort"
        rustup default nightly-x86_64-unknown-linux-gnu || warning "Can't set default toolchain!"
        rustup target add x86_64-unknown-none || fatal "Can't install target! Abort"
    fi
}

# TODO Rustc version, x86 on x86_64

# Call (May use additional arguments)
main "$4"