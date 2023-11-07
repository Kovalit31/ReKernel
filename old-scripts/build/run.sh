#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    cd "$BASEDIR/build"
    if [ "$1" == "debug" ]; then
        cd kernel/
        if [ -d "../image/" ]; then
            cd ../image/
        fi
        + "Error while running!" cargo run
    else
        cd kernel/
        if [ -d "../image/" ]; then
            cd ../image/
        fi
        + "Error while running!" cargo run --release
    fi
}

# Call (May use additional arguments)
main "$4"