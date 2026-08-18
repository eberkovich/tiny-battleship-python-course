from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_fake_python(directory: Path, name: str, *, compatible: bool) -> None:
    path = directory / name
    status = 0 if compatible else 1
    path.write_text(f"#!/bin/sh\nexit {status}\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _write_functional_fake_python(directory: Path, name: str = "python3") -> None:
    path = directory / name
    path.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"venv\" ]; then\n"
        "  /bin/mkdir -p \"$3/bin\"\n"
        "  /bin/cp \"$0\" \"$3/bin/python\"\n"
        "  exit 0\n"
        "fi\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"pip\" ]; then\n"
        "  exit \"${FAKE_PIP_STATUS:-0}\"\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _write_python_with_tk_without_idle(directory: Path) -> None:
    path = directory / "python3"
    path.write_text(
        "#!/bin/sh\n"
        "case \"$2\" in\n"
        "  *\"import tkinter, idlelib\"*) exit 1 ;;\n"
        "  *\"sys.version_info\"*) exit 0 ;;\n"
        "  *\"import tkinter\"*) exit 0 ;;\n"
        "  *\"import idlelib\"*) exit 1 ;;\n"
        "esac\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _write_homebrew_python_without_tk(directory: Path) -> Path:
    path = directory / "python3"
    path.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"venv\" ]; then\n"
        "  /bin/mkdir -p \"$3/bin\"\n"
        "  /bin/cp \"$0\" \"$3/bin/python\"\n"
        "  exit 0\n"
        "fi\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"pip\" ]; then\n"
        "  exit 0\n"
        "fi\n"
        "case \"$2\" in\n"
        "  *\"import tkinter\"*) [ -f \"$FAKE_TK_MARKER\" ]; exit $? ;;\n"
        "  *\"os.path.realpath\"*) echo \"$FAKE_PYTHON_PATH\"; exit 0 ;;\n"
        "  *\"sys.version_info.major\"*) echo \"3.13\"; exit 0 ;;\n"
        "  *\"sys.version_info\"*) exit 0 ;;\n"
        "esac\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def _run_check_only(script: Path, fake_bin: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PATH"] = str(fake_bin)
    environment["BATTLESHIP_INSTALL_CHECK_ONLY"] = "1"
    return subprocess.run(
        ["/bin/bash", str(script)],
        env=environment,
        text=True,
        capture_output=True,
        timeout=5,
    )


def test_shell_scripts_have_valid_syntax() -> None:
    for name in ("install.command", "run.command"):
        result = subprocess.run(
            ["/bin/bash", "-n", str(PROJECT_ROOT / name)], capture_output=True
        )
        assert result.returncode == 0, result.stderr


def test_installer_uses_pkgutil_status_not_localized_output(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    pkgutil = fake_bin / "pkgutil"
    pkgutil.write_text(
        "#!/bin/sh\n"
        'echo "Статус: пакет подписан доверенным сертификатом"\n'
        'exit "${FAKE_SIGNATURE_STATUS:-0}"\n',
        encoding="utf-8",
    )
    pkgutil.chmod(pkgutil.stat().st_mode | stat.S_IXUSR)
    package = tmp_path / "python.pkg"
    package.touch()
    command = (
        f'source "{PROJECT_ROOT / "install.command"}"; '
        f'verify_package_signature "{package}"'
    )
    environment = os.environ.copy()
    environment["PATH"] = str(fake_bin)

    trusted = subprocess.run(
        ["/bin/bash", "-c", command],
        env=environment,
        text=True,
        capture_output=True,
    )
    assert trusted.returncode == 0, trusted.stderr
    assert "Статус" in trusted.stdout

    environment["FAKE_SIGNATURE_STATUS"] = "1"
    untrusted = subprocess.run(
        ["/bin/bash", "-c", command],
        env=environment,
        text=True,
        capture_output=True,
    )
    assert untrusted.returncode != 0
    assert "доверенную подпись" in untrusted.stderr


def test_installer_accepts_python3_or_python_in_controlled_path(
    tmp_path: Path,
) -> None:
    script_dir = tmp_path / "Курс Python"
    script_dir.mkdir()
    script = script_dir / "install.command"
    shutil.copyfile(PROJECT_ROOT / "install.command", script)

    python3_bin = tmp_path / "python3-bin"
    python3_bin.mkdir()
    _write_fake_python(python3_bin, "python3", compatible=True)
    result = _run_check_only(script, python3_bin)
    assert result.returncode == 0
    assert "python3" in result.stdout

    python_bin = tmp_path / "python-bin"
    python_bin.mkdir()
    _write_fake_python(python_bin, "python", compatible=True)
    result = _run_check_only(script, python_bin)
    assert result.returncode == 0
    assert result.stdout.rstrip().endswith("/python")


def test_installer_rejects_python2_or_missing_python(tmp_path: Path) -> None:
    script = PROJECT_ROOT / "install.command"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_python(fake_bin, "python", compatible=False)

    result = _run_check_only(script, fake_bin)

    assert result.returncode != 0
    assert "Python 3.11–3.14" in result.stderr


def test_installer_rejects_python_without_idle_in_check_only_mode(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_python_with_tk_without_idle(fake_bin)

    result = _run_check_only(PROJECT_ROOT / "install.command", fake_bin)

    assert result.returncode != 0
    assert "Tk и IDLE" in result.stderr


def test_installer_finds_versioned_homebrew_python_without_python3_link(
    tmp_path: Path,
) -> None:
    homebrew_prefix = tmp_path / "homebrew"
    fake_bin = homebrew_prefix / "bin"
    fake_bin.mkdir(parents=True)
    brew = fake_bin / "brew"
    brew.write_text(
        "#!/bin/sh\n"
        f'echo "{homebrew_prefix}"\n',
        encoding="utf-8",
    )
    brew.chmod(brew.stat().st_mode | stat.S_IXUSR)
    versioned_bin = homebrew_prefix / "opt/python@3.13/bin"
    versioned_bin.mkdir(parents=True)
    _write_functional_fake_python(versioned_bin, "python3.13")

    result = _run_check_only(PROJECT_ROOT / "install.command", fake_bin)

    assert result.returncode == 0, result.stderr
    assert result.stdout.rstrip().endswith(
        "/opt/python@3.13/bin/python3.13"
    )
    assert "пароль администратора" not in result.stdout


def test_installer_adds_tk_to_supported_homebrew_python_without_sudo(
    tmp_path: Path,
) -> None:
    project = tmp_path / "Курс"
    project.mkdir()
    script = project / "install.command"
    shutil.copyfile(PROJECT_ROOT / "install.command", script)

    homebrew_prefix = tmp_path / "homebrew"
    fake_bin = homebrew_prefix / "bin"
    fake_bin.mkdir(parents=True)
    python = _write_homebrew_python_without_tk(fake_bin)
    marker = tmp_path / "tk-installed"
    brew_log = tmp_path / "brew.log"
    brew = fake_bin / "brew"
    brew.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"--prefix\" ]; then\n"
        "  echo \"$FAKE_BREW_PREFIX\"\n"
        "  exit 0\n"
        "fi\n"
        "if [ \"$1\" = \"install\" ]; then\n"
        "  echo \"$2\" > \"$FAKE_BREW_LOG\"\n"
        "  if [ \"${FAKE_BREW_STATUS:-0}\" -ne 0 ]; then\n"
        "    exit \"$FAKE_BREW_STATUS\"\n"
        "  fi\n"
        "  /usr/bin/touch \"$FAKE_TK_MARKER\"\n"
        "  exit 0\n"
        "fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    brew.chmod(brew.stat().st_mode | stat.S_IXUSR)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": str(fake_bin),
            "FAKE_BREW_PREFIX": str(homebrew_prefix),
            "FAKE_BREW_LOG": str(brew_log),
            "FAKE_PYTHON_PATH": str(python),
            "FAKE_TK_MARKER": str(marker),
        }
    )

    result = subprocess.run(
        ["/bin/bash", str(script)],
        env=environment,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert brew_log.read_text(encoding="utf-8").strip() == "python-tk@3.13"
    assert "без sudo" in result.stdout
    assert "пароль администратора" not in result.stdout
    assert (project / ".venv/bin/python").exists()

    marker.unlink()
    failed_project = tmp_path / "Курс с ошибкой Homebrew"
    failed_project.mkdir()
    failed_script = failed_project / "install.command"
    shutil.copyfile(PROJECT_ROOT / "install.command", failed_script)
    environment["FAKE_BREW_STATUS"] = "1"

    failed = subprocess.run(
        ["/bin/bash", str(failed_script)],
        env=environment,
        text=True,
        capture_output=True,
    )

    assert failed.returncode != 0
    assert "не менять Python по умолчанию" in failed.stderr
    assert "пароль администратора" not in failed.stdout
    assert not (failed_project / ".venv").exists()


def test_installer_is_repeatable_with_existing_environment(tmp_path: Path) -> None:
    project = tmp_path / "Курс с пробелом"
    project.mkdir()
    script = project / "install.command"
    shutil.copyfile(PROJECT_ROOT / "install.command", script)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_functional_fake_python(fake_bin)
    environment = os.environ.copy()
    environment["PATH"] = str(fake_bin)

    first = subprocess.run(
        ["/bin/bash", str(script)], env=environment, text=True, capture_output=True
    )
    second = subprocess.run(
        ["/bin/bash", str(script)], env=environment, text=True, capture_output=True
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert (project / ".venv/bin/python").exists()


def test_installer_reports_dependency_failure(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    script = project / "install.command"
    shutil.copyfile(PROJECT_ROOT / "install.command", script)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_functional_fake_python(fake_bin)
    environment = os.environ.copy()
    environment["PATH"] = str(fake_bin)
    environment["FAKE_PIP_STATUS"] = "1"

    result = subprocess.run(
        ["/bin/bash", str(script)], env=environment, text=True, capture_output=True
    )

    assert result.returncode != 0
    assert "Не удалось установить зависимости" in result.stderr


def test_installer_and_gitignore_track_stage_dependencies_and_output() -> None:
    installer = (PROJECT_ROOT / "install.command").read_text(encoding="utf-8")
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ignored = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "3.13.15" in installer
    assert "3b7eaf7f29825f796e8267024435540d" in installer
    for dependency in ("pygame-ce==2.5.8", "PyYAML==6.0.3"):
        assert dependency in pyproject
    assert "thonny" not in pyproject.lower()
    assert "import tkinter, idlelib" in installer
    assert "pip uninstall -y thonny" in installer
    assert "ensure_idle_config" in installer
    for generated in (".venv/", "students/", "screenshots/"):
        assert generated in ignored


def test_run_wrapper_requires_local_environment(tmp_path: Path) -> None:
    script = tmp_path / "run.command"
    shutil.copyfile(PROJECT_ROOT / "run.command", script)

    result = subprocess.run(
        ["/bin/bash", str(script), "--student-dir", "Иван"],
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "install.command" in result.stderr
