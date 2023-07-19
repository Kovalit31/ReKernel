#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"


# Logger
log() {
    ( echo -e "\n$1" | tee -a -i $LOGGER ) > /dev/null
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
        rm "$BASEDIR/build/build.py"
        log "Successfully created build dir!" 
    else
        log "Build dir already exists, skipping..."
    fi
    cd "$BASEDIR/build"
    if [ "$2" == "legacy" ]; then
        if [ ! -f "Cargo.toml" ]; then
            cp "configs/$2/$1/cargo.toml" Cargo.toml
        fi
        if [ ! -d ".cargo" ]; then
            mkdir .cargo
        fi
        if [ ! -f ".cargo/config.toml" ]; then
            cp "configs/$2/$1/config.toml" .cargo
        fi
        if [ ! -f "target.json" ]; then
            cp "configs/all/$1/target.json" .
        fi
        exit
    fi
    if [ ! -d "kernel" ]; then
        if [ ! -d "boot_target" ] || [ ! -d "kernel_patch" ]; then
            fatal "No necessary dir found, abort"
        fi
        mkdir kernel
        mv src/ build.rs kernel/
        mv boot_target src
        mv src/build.rs .
        mv kernel_patch/main.rs kernel/src
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
    if [ ! -f "Cargo.toml" ]; then
        cp "configs/$2/$1/cargo.toml" Cargo.toml
    fi
    if [ ! -d ".cargo" ]; then
        mkdir .cargo
    fi
    if [ ! -f ".cargo/config.toml" ]; then
        cp "configs/$2/$1/config.toml" .cargo/config.toml
    fi
    if [ ! -f "target.json" ]; then
        cp "configs/all/$1/target.json" target.json
    fi
}

# Call (May use additional arguments)
main "$4" "$5"