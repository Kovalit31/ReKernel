# Logger
function log() {
    (echo -e "\n$1" | tee -a -i $LOGGER) > /dev/null
}

function +() {
    ( ${@:2} || fatal "$1" ) > >( tee -a -i "$LOGGER" ) 2>&1
}

# Fatal trap. CAUTION: Kills parrent and stop executing!
function fatal() {
    log "$1"
    kill -SIGTERM $PARENT_PID
    exit 1
}