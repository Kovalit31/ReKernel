#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

. $BASEDIR/scripts/core/lib.sh

# Lifecycle
main() {
    "$BASEDIR/scripts/core/cmd_chk.sh" "$PARENT_PID" "$BASEDIR" "$LOGGER" "rustup" && exit 0
    "$BASEDIR/scripts/core/cmd_chk.sh" "$PARENT_PID" "$BASEDIR" "$LOGGER" "wget" || fatal "Wget not found. Abort"
    + "Rustup installator download error. Abort" /bin/bash -c "wget -O- http://sh.rustup.rs | sh -s -- -y --profile minimal"
    rustup set profile default || log "Can't set default toolchain profile!"
}

# Call (May use additional arguments)
main