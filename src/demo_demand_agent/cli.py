from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data"
DEFAULT_WORKSPACE_ROOT = PROJECT_ROOT / "examples" / "workspaces"

REQUIRED_FIELDS = (
    "title",
    "business_question",
    "metric",
    "grain",
    "time_window",
    "acceptance_criteria",
)


def _read_yaml(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_catalog(data_root: Path) -> dict[str, Any]:
    return _read_yaml(data_root / "catalog.json")


def _load_lineage(data_root: Path) -> dict[str, Any]:
    return _read_yaml(data_root / "lineage.json")


def _workspace_name(title: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in title).strip("_")
    return clean or "demo_demand"


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def metadata_tables(data_root: Path = DEFAULT_DATA_ROOT) -> None:
    """List synthetic tables from the demo catalog."""
    catalog = _load_catalog(data_root)
    print("Synthetic Catalog")
    print("table\towner\tdescription")
    for name, item in sorted(catalog.get("tables", {}).items()):
        print(f"{name}\t{item.get('owner', '')}\t{item.get('description', '')}")


def metadata_schema(table_name: str, data_root: Path = DEFAULT_DATA_ROOT) -> int:
    """Show a synthetic table schema."""
    catalog = _load_catalog(data_root)
    item = catalog.get("tables", {}).get(table_name)
    if not item:
        print(f"Unknown table: {table_name}", file=sys.stderr)
        return 1
    print(f"Schema: {table_name}")
    print("column\ttype\tdescription")
    for col in item.get("columns", []):
        print(f"{col['name']}\t{col['type']}\t{col.get('description', '')}")
    return 0


def metadata_lineage(table_name: str, data_root: Path = DEFAULT_DATA_ROOT) -> None:
    """Show upstream tables for a synthetic target table."""
    lineage = _load_lineage(data_root)
    upstream = lineage.get("lineage", {}).get(table_name, [])
    if not upstream:
        print(f"No upstream lineage found for {table_name}")
        return
    print(f"Lineage: {table_name}")
    print("target\tupstream")
    for item in upstream:
        print(f"{table_name}\t{item}")


def demand_new(
    request_file: Path,
    data_root: Path = DEFAULT_DATA_ROOT,
    workspace_root: Path = DEFAULT_WORKSPACE_ROOT,
) -> int:
    """Create public-safe demand artifacts from a synthetic request."""
    request = _read_yaml(request_file)
    missing = [field for field in REQUIRED_FIELDS if not str(request.get(field, "")).strip()]
    workspace = workspace_root / _workspace_name(str(request.get("title", "")))
    workspace.mkdir(parents=True, exist_ok=True)

    requirement = (
        "# Requirement\n\n"
        f"## Business Question\n{request.get('business_question', '')}\n\n"
        f"## Metric\n{request.get('metric', '')}\n\n"
        f"## Grain\n{request.get('grain', '')}\n\n"
        f"## Time Window\n{request.get('time_window', '')}\n\n"
        f"## Acceptance Criteria\n{request.get('acceptance_criteria', '')}\n"
    )
    (workspace / "requirement.md").write_text(requirement, encoding="utf-8")

    catalog = _load_catalog(data_root)
    lineage = _load_lineage(data_root)
    target_table = str(request.get("target_table", "mart.refund_metrics_daily"))
    target_schema = catalog.get("tables", {}).get(target_table, {})
    upstream = lineage.get("lineage", {}).get(target_table, [])

    evidence = {
        "evidence_type": "synthetic_metadata_check",
        "target_table": target_table,
        "target_columns": [col["name"] for col in target_schema.get("columns", [])],
        "upstream_tables": upstream,
        "sample_policy": "synthetic-only",
        "request_hash": _hash_text(requirement),
    }
    _write_yaml(workspace / "evidence.yaml", evidence)

    analysis = (
        "# Analysis\n\n"
        "## Selected Approach\n"
        f"Build `{target_table}` from synthetic upstream tables: {', '.join(upstream)}.\n\n"
        "## Validation Plan\n"
        "- Check required columns exist in catalog.\n"
        "- Compare row counts by date.\n"
        "- Validate null rates for metric fields.\n"
        "- Store only synthetic samples and aggregate evidence.\n"
    )
    (workspace / "analysis.md").write_text(analysis, encoding="utf-8")

    status = "blocked" if missing else "ready"
    _write_yaml(
        workspace / "status.yaml",
        {
            "status": status,
            "missing_fields": missing,
            "artifacts": ["requirement.md", "analysis.md", "evidence.yaml"],
        },
    )
    print(f"Workspace created: {workspace}")
    print(f"status={status}")
    return 0


def validate_workspace(workspace: Path) -> int:
    """Validate that a demand workspace has the expected public-safe artifacts."""
    required = ["requirement.md", "analysis.md", "evidence.yaml", "status.yaml"]
    missing = [name for name in required if not (workspace / name).exists()]
    if missing:
        print(f"Missing artifacts: {', '.join(missing)}", file=sys.stderr)
        return 1
    evidence = _read_yaml(workspace / "evidence.yaml")
    if evidence.get("sample_policy") != "synthetic-only":
        print("Evidence must be synthetic-only", file=sys.stderr)
        return 1
    print("Workspace validation passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="demo-demand-agent")
    sub = parser.add_subparsers(dest="command", required=True)

    metadata = sub.add_parser("metadata")
    metadata_sub = metadata.add_subparsers(dest="metadata_command", required=True)
    metadata_sub.add_parser("tables")
    schema = metadata_sub.add_parser("schema")
    schema.add_argument("table_name")
    lineage = metadata_sub.add_parser("lineage")
    lineage.add_argument("table_name")

    demand = sub.add_parser("demand")
    demand_sub = demand.add_subparsers(dest="demand_command", required=True)
    new_demand = demand_sub.add_parser("new")
    new_demand.add_argument("request_file", type=Path)
    new_demand.add_argument("--workspace-root", type=Path, default=DEFAULT_WORKSPACE_ROOT)
    new_demand.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)

    validate = sub.add_parser("validate")
    validate.add_argument("workspace", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "metadata":
        if args.metadata_command == "tables":
            metadata_tables()
            return 0
        if args.metadata_command == "schema":
            return metadata_schema(args.table_name)
        if args.metadata_command == "lineage":
            metadata_lineage(args.table_name)
            return 0
    if args.command == "demand" and args.demand_command == "new":
        return demand_new(args.request_file, args.data_root, args.workspace_root)
    if args.command == "validate":
        return validate_workspace(args.workspace)
    return 1


def app() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
