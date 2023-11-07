#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    if [ "$1" = "x86_64" ]; then
        + "Can't install toolchain!" rustup toolchain install nightly-x86_64-unknown-linux-gnu
        rustup default nightly-x86_64-unknown-linux-gnu || warning "Can't set default toolchain!"
        + "Can't install target!" rustup target add x86_64-unknown-none
    fi
}

# Call (May use additional arguments)
main "$4"