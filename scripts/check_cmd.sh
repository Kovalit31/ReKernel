#!/bin/bash

PARENT_PID="$1"
BASEDIR="$2"
LOGGER="$3"

log() {
    (echo "$1" | tee -a -i $LOGGER) > /dev/null
}

fatal() {
    log "$1"
    kill -SIGTERM $PARENT_PID
    exit 1
}

check_cmd() {
    if [ -z ${1+x} ]; then 
        fatal "\$1 is unsetted! Can't check command"
    fi
    (command -v $1 &> /dev/null) || fatal "$1: command not found"
}

check_cmd "$4"