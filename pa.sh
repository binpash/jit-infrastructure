#!/usr/bin/env bash

export PASH_TOP=${PASH_TOP:-${BASH_SOURCE%/*}}
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib/"
export PYTHONPATH="${PASH_TOP}/python_pkgs/:${PYTHONPATH}"

trap kill_all SIGTERM SIGINT
kill_all() {
    kill -s SIGKILL 0
}

old_umask=$(umask)
umask u=rwx,g=rx,o=rx

if ! command -v python3 &> /dev/null; then
    echo "Python >=3 could not be found"
    exit
fi

export PASH_BASH_VERSION="${BASH_VERSINFO[@]:0:3}"

umask "$old_umask"
PASH_FROM_SH="pa.sh" python3 -S "$PASH_TOP/compiler/pash.py" "$@"
pash_exit_code=$?


(exit "$pash_exit_code")
