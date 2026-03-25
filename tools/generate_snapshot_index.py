import json
import pathlib
import sys


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    snapshot_dir = root / "tests" / "snapshots"
    summary_files = sorted(path for path in snapshot_dir.glob("*.summary.json"))

    entries = []
    for path in summary_files:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        entries.append(
            {
                "file": path.name,
                "module": payload["module"],
                "export_count": len(payload.get("exports", [])),
                "type_count": len(payload.get("types", [])),
            }
        )

    inventory = {
        "schema_version": "0.1.0",
        "generated_from": "tests/snapshots/*.summary.json",
        "snapshots": entries,
    }

    output_path = snapshot_dir / "index.json"
    output_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
