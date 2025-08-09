#!/bin/sh
# Use: ./wait-for-it.sh host:port [-s] [-t timeout] [-- command args]
# -s : strict (exit if test fails)
# -q : quiet
# -t TIMEOUT : timeout in seconds, zero for no timeout
# -- COMMAND ARGS : command to execute after success

TIMEOUT=15
QUIET=0
STRICT=0
HOST=""
PORT=""
COMMAND=""

wait_for() {
    for i in `seq $TIMEOUT` ; do
        nc -z "$HOST" "$PORT" > /dev/null 2>&1
        if [ $? -eq 0 ] ; then
            if [ $QUIET -ne 1 ] ; then echo " $HOST:$PORT is available after $i seconds"; fi
            return 0
        fi
        sleep 1
    done
    echo "Operation timed out"
    return 1
}

while [ $# -gt 0 ]; do
    case "$1" in
        *:* )
        HOST=${1%%:*}
        PORT=${1##*:}
        shift 1
        ;;
        -q | --quiet)
        QUIET=1
        shift 1
        ;;
        -s | --strict)
        STRICT=1
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        shift 2
        ;;
        --timeout=*)
        TIMEOUT="${1#*=}"
        shift 1
        ;;
        --)
        shift
        COMMAND="$@"
        break
        ;;
        *)
        echo "Unknown argument: $1"
        exit 1
        ;;
    esac
done

wait_for
RESULT=$?
if [ $RESULT -eq 1 -a $STRICT -eq 1 ] ; then
    exit 1
fi
if [ -n "$COMMAND" ] ; then
    exec $COMMAND
fi
exit $RESULT