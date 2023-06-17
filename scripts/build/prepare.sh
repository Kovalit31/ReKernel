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
    if [ ! -d "$BASEDIR/build" ]; then
        data=$(ls "$BASEDIR")
        mkdir -p "$BASEDIR/build"
        for x in $data; do cp -r "$BASEDIR/$x" "$BASEDIR/build"; done
    else
        log "Build dir already exists, skipping"
    fi
    cd "$BASEDIR/build"
    if [ ! -f "Cargo.toml" ]; then
        cp "configs/Cargo.$1.$2.toml" Cargo.toml
    fi
    if [ ! -d ".cargo" ]; then
        mkdir .cargo
        cp "configs/$1.$2.toml" .cargo/config.toml
    fi
    if [ ! -f "target.json" ]; then
        cp "configs/$1.target.json" target.json
    fi
}

# Call (May use additional arguments)
main "$4" "$5"