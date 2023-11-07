function check_var() {
    if [ -z "$1" ]; then
        return 1
    fi
    return 0
}

check_var $LOGGER || exit 1
check_var $PARENT_ID || exit 1

function +() {
    ( ${@:2} || fatal "$1" ) > >( tee -a -i "$LOGGER" ) 2>&1
}

## Logger
function log() {
    (echo -e "\n$1" | tee -a -i $LOGGER) > /dev/null
}

## Print level 
function fatal() {
    log "[&] $1"
    kill -SIGTERM $PARENT_PID
    exit 1
}

function error() {
    log "[@] $1"
    exit 1
}

function warn() {
    log "[!] $1"
}

function info() {
    log "[*] $1"
}

function check_cmd() {
    (command -v $1 &> /dev/null) || (log "$1: command not found!" && return 1)
}