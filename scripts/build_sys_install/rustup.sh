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
    "$BASEDIR/scripts/core/cmd_chk.sh" "$PARENT_PID" "$BASEDIR" "$LOGGER" "wget"
    if [ $? -ne 0 ]; then
        log "Wget not found. Abort"
        exit 2
    fi
    (wget -O- http://sh.rustup.rs | sh -s -- -y --profile minimal) || fatal "Rustup installation error occured. Abort"
    rustup set profile default || log "Can't set default toolchain profile!"
}

# Call (May use additional arguments)
main