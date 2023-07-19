#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

# Logger
log() {
    (echo -e "\n$1" | tee -a -i $LOGGER) > /dev/null
}

exec_log() {
    $@ > >( tee -a -i "$LOGGER" ) 2>&1
}

# Fatal trap. CAUTION: Kills parrent and stop executing!
fatal() {
    log "$1"
    kill -SIGTERM $PARENT_PID
    exit 1
}

# Lifecycle
main() {
    "$BASEDIR/scripts/core/cmd_chk.sh" "$PARENT_PID" "$BASEDIR" "$LOGGER" "rustup" && exit 0
    "$BASEDIR/scripts/core/cmd_chk.sh" "$PARENT_PID" "$BASEDIR" "$LOGGER" "wget" || fatal "Wget not found. Abort"
    (wget -O- http://sh.rustup.rs | sh -s -- -y --profile minimal) || fatal "Rustup installator download error. Abort"
    rustup set profile default || log "Can't set default toolchain profile!"
}

# Call (May use additional arguments)
main