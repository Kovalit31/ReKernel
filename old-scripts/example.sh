#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    + "It can't be raised! ._." echo "Hello world!"
}

# Call (May use additional arguments)
main