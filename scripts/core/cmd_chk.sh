#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    if [ -z ${1+x} ]; then 
        fatal "\$1 is unsetted! Can't check command"
    fi
    (command -v $1 &> /dev/null) || fatal "$1: command not found"
}

# Call (May use additional arguments)
main "$4"