#!/bin/bash

set -u

PROJECT_DIR="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=11
OFFICIAL_PYTHON_VERSION=3.13.15
OFFICIAL_PYTHON_URL="https://www.python.org/ftp/python/${OFFICIAL_PYTHON_VERSION}/python-${OFFICIAL_PYTHON_VERSION}-macos11.pkg"
OFFICIAL_PYTHON_SHA256="3b7eaf7f29825f796e8267024435540ddf1f17fc9a97ad58095daa7a75bfdcd3"
VENV_DIR="$PROJECT_DIR/.venv"
INSTALL_TMP_DIR=""

fail() {
    echo "Ошибка установки: $1" >&2
    exit 1
}

cleanup() {
    if [[ -n "$INSTALL_TMP_DIR" && -d "$INSTALL_TMP_DIR" ]]; then
        /bin/rm -rf "$INSTALL_TMP_DIR"
    fi
}

trap cleanup EXIT

python_is_compatible() {
    local candidate="$1"
    "$candidate" -c "import sys; assert (${MIN_PYTHON_MAJOR}, ${MIN_PYTHON_MINOR}) <= sys.version_info < (3, 15); import tkinter" >/dev/null 2>&1
}

python_version_is_supported() {
    local candidate="$1"
    "$candidate" -c "import sys; assert (${MIN_PYTHON_MAJOR}, ${MIN_PYTHON_MINOR}) <= sys.version_info < (3, 15)" >/dev/null 2>&1
}

find_compatible_python() {
    local command_name
    local candidate
    local brew_prefix
    local minor
    for command_name in python3 python; do
        candidate="$(command -v "$command_name" 2>/dev/null || true)"
        if [[ -n "$candidate" ]] && python_is_compatible "$candidate"; then
            echo "$candidate"
            return 0
        fi
    done
    if command -v brew >/dev/null 2>&1; then
        brew_prefix="$(brew --prefix 2>/dev/null || true)"
        if [[ -n "$brew_prefix" ]]; then
            for minor in 13 14 12 11; do
                candidate="$brew_prefix/opt/python@3.${minor}/bin/python3.${minor}"
                if [[ -x "$candidate" ]] && python_is_compatible "$candidate"; then
                    echo "$candidate"
                    return 0
                fi
            done
        fi
    fi
    return 1
}

find_supported_python() {
    local command_name
    local candidate
    local brew_prefix
    local minor
    for command_name in python3 python; do
        candidate="$(command -v "$command_name" 2>/dev/null || true)"
        if [[ -n "$candidate" ]] && python_version_is_supported "$candidate"; then
            echo "$candidate"
            return 0
        fi
    done
    if command -v brew >/dev/null 2>&1; then
        brew_prefix="$(brew --prefix 2>/dev/null || true)"
        if [[ -n "$brew_prefix" ]]; then
            for minor in 13 14 12 11; do
                candidate="$brew_prefix/opt/python@3.${minor}/bin/python3.${minor}"
                if [[ -x "$candidate" ]] && python_version_is_supported "$candidate"; then
                    echo "$candidate"
                    return 0
                fi
            done
        fi
    fi
    return 1
}

install_homebrew_tk() {
    local candidate="$1"
    local brew_prefix
    local python_path
    local python_minor
    local formula

    command -v brew >/dev/null 2>&1 || return 2
    brew_prefix="$(brew --prefix 2>/dev/null)" || return 2
    python_path="$("$candidate" -c 'import os, sys; print(os.path.realpath(sys.executable))' 2>/dev/null)" || return 2
    case "$python_path" in
        "$brew_prefix"/*) ;;
        *) return 2 ;;
    esac

    python_minor="$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)" || return 2
    formula="python-tk@${python_minor}"
    echo "Найден Homebrew Python ${python_minor} без Tk."
    echo "Устанавливаю ${formula} через Homebrew без sudo…"
    brew install "$formula" || return 1
    python_is_compatible "$candidate"
}

install_official_python() {
    [[ "$(uname -s)" == "Darwin" ]] || fail "Python 3.11–3.14 с Tk не найден. Автоматическая установка поддерживается только на macOS."
    command -v curl >/dev/null 2>&1 || fail "Не найдена команда curl."
    command -v shasum >/dev/null 2>&1 || fail "Не найдена команда shasum."
    command -v pkgutil >/dev/null 2>&1 || fail "Не найдена команда pkgutil."
    command -v sudo >/dev/null 2>&1 || fail "Не найдена команда sudo."

    INSTALL_TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/tiny-battleship-install.XXXXXX")" || fail "Не удалось создать временную папку."
    local package_path="$INSTALL_TMP_DIR/python.pkg"

    echo "Загружаю официальный Python ${OFFICIAL_PYTHON_VERSION}…"
    curl --fail --location --retry 3 --output "$package_path" "$OFFICIAL_PYTHON_URL" \
        || fail "Не удалось загрузить Python с python.org."

    echo "${OFFICIAL_PYTHON_SHA256}  ${package_path}" | shasum -a 256 --check - \
        || fail "Контрольная сумма установщика Python не совпала."

    verify_package_signature "$package_path"

    echo "macOS попросит пароль администратора для установки Python."
    sudo /usr/sbin/installer -pkg "$package_path" -target / \
        || fail "macOS не смогла установить Python."
}

verify_package_signature() {
    pkgutil --check-signature "$1" \
        || fail "Не удалось подтвердить доверенную подпись установщика Python."
}

main() {
    local homebrew_tk_status
    local python_bin
    local supported_python
    python_bin="$(find_compatible_python || true)"

    if [[ -z "$python_bin" && "${BATTLESHIP_INSTALL_CHECK_ONLY:-0}" == "1" ]]; then
        fail "Python 3.11–3.14 с поддержкой Tk не найден."
    fi

    if [[ -z "$python_bin" ]]; then
        supported_python="$(find_supported_python || true)"
        if [[ -n "$supported_python" ]]; then
            homebrew_tk_status=0
            install_homebrew_tk "$supported_python" || homebrew_tk_status=$?
            case "$homebrew_tk_status" in
                0)
                    python_bin="$(find_compatible_python || true)"
                    [[ -n "$python_bin" ]] || fail "Homebrew установил Tk, но подходящий Python не найден."
                    ;;
                1)
                    python_bin="$(find_compatible_python || true)"
                    if [[ -z "$python_bin" ]]; then
                        fail "Homebrew не смог добавить Tk. Установка остановлена, чтобы не менять Python по умолчанию. Исправь ошибку Homebrew выше и запусти install.command ещё раз."
                    fi
                    echo "Homebrew сообщил об ошибке, но Python с Tk установлен. Продолжаю без системного установщика."
                    ;;
                2) ;;
                *) fail "Неожиданная ошибка при проверке Homebrew Python." ;;
            esac
        fi
    fi

    if [[ -z "$python_bin" ]]; then
        install_official_python
        for candidate in \
            "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3" \
            "/usr/local/bin/python3"; do
            if [[ -x "$candidate" ]] && python_is_compatible "$candidate"; then
                python_bin="$candidate"
                break
            fi
        done
        [[ -n "$python_bin" ]] || fail "Python установлен, но команда python3 не найдена. Перезагрузи Mac и повтори установку."
    fi

    if [[ "${BATTLESHIP_INSTALL_CHECK_ONLY:-0}" == "1" ]]; then
        echo "Подходящий Python найден: $python_bin"
        exit 0
    fi

    if [[ -x "$VENV_DIR/bin/python" ]] && ! python_is_compatible "$VENV_DIR/bin/python"; then
        /bin/rm -rf "$VENV_DIR"
    fi

    if [[ ! -x "$VENV_DIR/bin/python" ]]; then
        echo "Создаю окружение курса…"
        "$python_bin" -m venv "$VENV_DIR" || fail "Не удалось создать окружение .venv."
    fi

    echo "Устанавливаю зависимости курса…"
    "$VENV_DIR/bin/python" -m pip install -e "$PROJECT_DIR[test]" \
        || fail "Не удалось установить зависимости. Проверь подключение к интернету."

    "$VENV_DIR/bin/python" -c "import tkinter, pygame, yaml, thonny, battleship_ui, launcher" \
        || fail "Проверка зависимостей завершилась ошибкой."

    "$VENV_DIR/bin/python" -c "from launcher.editor import ensure_russian_thonny_config; ensure_russian_thonny_config()" \
        || fail "Не удалось настроить русский интерфейс Thonny."

    echo
    echo "Установка завершена."
    echo "Запусти курс командой:"
    echo "  \"$PROJECT_DIR/run.command\" --student-dir \"$PROJECT_DIR/students/имя_ребёнка\""
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
