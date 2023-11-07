#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    check_cmd "rustup" && exit 0
    check_cmd "wget" || fatal "Wget not found. Abort"
    + "Rustup installator download error. Abort" /bin/bash -c "wget -O- http://sh.rustup.rs | sh -s -- -y --profile minimal"
    rustup set profile default || log "Can't set default toolchain profile!"
}

# Call (May use additional arguments)
main