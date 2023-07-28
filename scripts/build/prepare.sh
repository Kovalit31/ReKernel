#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"


. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    if [ ! -d "$BASEDIR/build" ]; then
        data=$(ls "$BASEDIR")
        mkdir -p "$BASEDIR/build"
        for x in $data; do cp -r "$BASEDIR/$x" "$BASEDIR/build"; done
        rm "$BASEDIR/build/build.py"
        log "Successfully created build dir!" 
    else
        log "Build dir already exists, skipping..."
    fi
    cd "$BASEDIR/build"
    # DEFAULT
    if [ ! -d "kernel" ]; then
        fatal "No kernel dir found, abort"
    fi
    if [ ! -d "kernel/.cargo" ]; then
        mkdir kernel/.cargo
    fi
    if [ ! -f "kernel/.cargo/config.toml" ]; then
        cp "configs/$2/$1/config_kernel.toml" kernel/.cargo/config.toml
    fi
    if [ ! -f "kernel/Cargo.toml" ]; then
        cp "configs/$2/$1/cargo_kernel.toml" "kernel/Cargo.toml"
    fi
    if [ ! -f "kernel/target.json" ]; then
        cp "configs/all/$1/target.json" "kernel/"
    fi
    if [ "$2" == "legacy" ]; then
        rm -rf image/
        exit 0
    fi
    mv kernel/patch/* kernel/src
    if [ ! -f "image/Cargo.toml" ]; then
        cp "configs/$2/$1/cargo.toml" image/Cargo.toml
    fi
    if [ ! -d "image/.cargo" ]; then
        mkdir image/.cargo
    fi
    if [ ! -f "image/.cargo/config.toml" ]; then
        cp "configs/$2/$1/config.toml" image/.cargo/config.toml
    fi
    if [ ! -f "image/target.json" ] || [ ! -f "kernel/target.json" ]; then
        cp "configs/all/$1/target.json" image/target.json
        cp "configs/all/$1/target.json" kernel/target.json
    fi
}

# Call (May use additional arguments)
main "$4" "$5"