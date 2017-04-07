#!/bin/bash

mkdir LOGS
mount /dev/sdb1 LOGS

cd `dirname $0`

source venv/bin/activate

./run_meters.py 60


