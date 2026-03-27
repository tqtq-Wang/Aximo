from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import sys

if sys.platform == "win32":
    import winreg

LLVM_TOOL_NAMES: tuple[str, ...] = ("clang", "llc", "opt", "llvm-as", "lli")


@dataclass(frozen=True)
class ToolStatus:
    name: str
    path: str | None
    version: str | None
    error: str | None = None

    @property
    def available(self) -> bool:
        return self.path is not None


@dataclass(frozen=True)
class ToolchainReport:
    tools: tuple[ToolStatus, ...]

    @property
    def available_count(self) -> int:
        return sum(1 for tool in self.tools if tool.available)

    @property
    def total_count(self) -> int:
        return len(self.tools)

    @property
    def status(self) -> str:
        if self.available_count == self.total_count:
            return "full"
        if self.available_count == 0:
            return "missing"
        return "partial"

    @property
    def syntax_validation_ready(self) -> bool:
        return any(tool.name == "llvm-as" and tool.available for tool in self.tools)

    @property
    def execution_ready(self) -> bool:
        return any(tool.name in {"clang", "lli"} and tool.available for tool in self.tools)


def probe_tool(name: str) -> ToolStatus:
    resolved = shutil.which(name, path=_candidate_search_path())
    if resolved is None:
        return ToolStatus(name=name, path=None, version=None)
    version, error = _read_version(Path(resolved))
    return ToolStatus(name=name, path=resolved, version=version, error=error)


def probe_toolchain() -> ToolchainReport:
    return ToolchainReport(tools=tuple(probe_tool(name) for name in LLVM_TOOL_NAMES))


def format_toolchain_report(report: ToolchainReport) -> str:
    lines = [
        "LLVM toolchain check",
        f"status: {report.status} ({report.available_count}/{report.total_count} tools found)",
    ]
    for tool in report.tools:
        if not tool.available:
            lines.append(f"- {tool.name}: missing")
            continue
        lines.append(f"- {tool.name}: {tool.path}")
        if tool.version:
            lines.append(f"  version: {tool.version}")
        if tool.error:
            lines.append(f"  warning: {tool.error}")
    lines.append(
        "syntax_validation: "
        + ("ready via llvm-as" if report.syntax_validation_ready else "not ready")
    )
    lines.append(
        "demo_execution: "
        + ("possible via clang/lli" if report.execution_ready else "not ready")
    )
    return "\n".join(lines)


def _read_version(path: Path) -> tuple[str | None, str | None]:
    try:
        completed = subprocess.run(
            [str(path), "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
        )
    except OSError as error:
        return None, f"failed to launch: {error}"
    except subprocess.TimeoutExpired:
        return None, "timed out while reading version"

    output = completed.stdout or completed.stderr
    version_line = next((line.strip() for line in output.splitlines() if line.strip()), None)
    if completed.returncode != 0:
        message = f"--version exited with code {completed.returncode}"
        if version_line is not None:
            return version_line, message
        return None, message
    return version_line, None


def _candidate_search_path() -> str | None:
    segments: list[str] = []
    seen: set[str] = set()

    for path_value in (os.environ.get("PATH"), _read_windows_path("user"), _read_windows_path("machine")):
        if not path_value:
            continue
        for raw_segment in path_value.split(os.pathsep):
            segment = raw_segment.strip()
            if not segment:
                continue
            normalized = os.path.normcase(os.path.normpath(os.path.expandvars(segment)))
            if normalized in seen:
                continue
            seen.add(normalized)
            segments.append(os.path.expandvars(segment))

    if not segments:
        return None
    return os.pathsep.join(segments)


def _read_windows_path(scope: str) -> str | None:
    if sys.platform != "win32":
        return None

    hive = winreg.HKEY_CURRENT_USER if scope == "user" else winreg.HKEY_LOCAL_MACHINE
    sub_key = (
        r"Environment"
        if scope == "user"
        else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    )
    try:
        with winreg.OpenKey(hive, sub_key) as key:
            value, _ = winreg.QueryValueEx(key, "Path")
    except FileNotFoundError:
        return None
    except OSError:
        return None
    if not isinstance(value, str):
        return None
    return value
