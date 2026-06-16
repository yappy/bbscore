#!/bin/sh
set -eu

cd "$(dirname "$0")"

pip install -r requirements.txt
pip freeze > requirements.lock
