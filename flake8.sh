#!/bin/sh
set -eu

cd "$(dirname "$0")"

flake8 --benchmark
