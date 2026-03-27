from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess

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
    resolved = shutil.which(name)
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
