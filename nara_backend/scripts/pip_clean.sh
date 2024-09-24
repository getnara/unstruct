#!/bin/sh

REQUIREMENTS_FILE=$(dirname "$BASH_SOURCE")/../requirements.txt
pip freeze | grep -v -f requirements.txt - | grep -v '^#' | xargs pip uninstall -y

exec "$@"
