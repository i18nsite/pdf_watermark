#!/usr/bin/env bash

set -e
DIR=$(realpath $0) && DIR=${DIR%/*}
cd $DIR
set -x

if ! ls input/*.pdf >/dev/null 2>&1; then
  cp done/*.pdf input/
fi

python main.py
