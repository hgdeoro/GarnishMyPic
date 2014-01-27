#!/bin/bash

BASEDIR=$(cd $(dirname $0); pwd)

. $BASEDIR/virtualenv/bin/activate

export PYTHONPATH=$BASEDIR:$PYTHONPATH

python $BASEDIR/garnish.py "$@"
