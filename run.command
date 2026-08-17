#!/bin/bash

set -u

PROJECT_DIR="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Курс ещё не установлен. Сначала запусти install.command." >&2
    exit 1
fi

exec "$PYTHON_BIN" -m launcher "$@"

