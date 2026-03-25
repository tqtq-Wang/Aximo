import pathlib
import re
import sys


def expected_module(path: pathlib.Path) -> str:
    src_root = next(parent for parent in path.parents if parent.name == "src")
    rel = path.relative_to(src_root)
    return ".".join(rel.with_suffix("").parts)


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]

    required_example_files = [
        "examples/hello-world/axiom.toml",
        "examples/hello-world/src/app.ax",
        "examples/user-service/axiom.toml",
        "examples/user-service/src/app.ax",
        "examples/user-service/src/domain/user/model.ax",
        "examples/user-service/src/domain/user/errors.ax",
        "examples/user-service/src/domain/user/repo.ax",
        "examples/user-service/src/domain/user/service.ax",
        "examples/user-service/src/domain/user/tests.ax",
        "examples/effect-demo/axiom.toml",
        "examples/effect-demo/src/app.ax",
    ]

    missing = [path for path in required_example_files if not (root / path).exists()]
    if missing:
        raise SystemExit("missing example files:\n- " + "\n- ".join(missing))

    module_pattern = re.compile(r"^\s*module\s+([A-Za-z_][A-Za-z0-9_\.]*)\s*$")

    for path in (root / "examples").glob("**/src/**/*.ax"):
        text = path.read_text(encoding="utf-8")
        first_line = next((line for line in text.splitlines() if line.strip()), "")
        match = module_pattern.match(first_line)
        if not match:
            raise SystemExit(f"missing module declaration: {path}")
        found = match.group(1)
        expected = expected_module(path)
        if found != expected:
            raise SystemExit(f"module path mismatch in {path}: expected {expected}, got {found}")

    snapshot_files = {
        "hello-world": root / "tests" / "snapshots" / "hello-world.summary.json",
        "user-service": root / "tests" / "snapshots" / "user-service.summary.json",
        "effect-demo": root / "tests" / "snapshots" / "effect-demo.summary.json",
    }
    missing_snapshots = [name for name, path in snapshot_files.items() if not path.exists()]
    if missing_snapshots:
        raise SystemExit("missing snapshots:\n- " + "\n- ".join(missing_snapshots))

    effect_demo = (root / "examples" / "effect-demo" / "src" / "app.ax").read_text(encoding="utf-8")
    if "pub async fn send_message" not in effect_demo or "effects [net.call, log.write]" not in effect_demo:
        raise SystemExit("effect-demo example no longer demonstrates the required async/effect combination")

    print("validated example inventory, module path mapping, and required snapshots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
