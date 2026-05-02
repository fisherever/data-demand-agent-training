from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "demo_demand_agent.cli", *args],
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
    )


def test_demand_new_creates_public_safe_workspace(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspaces"
    result = run_cli(
        "demand",
        "new",
        "examples/requests/refund_metrics.json",
        "--workspace-root",
        str(workspace_root),
    )

    assert result.returncode == 0
    workspace = workspace_root / "refund_metrics"
    assert (workspace / "requirement.md").exists()
    assert (workspace / "analysis.md").exists()
    assert (workspace / "evidence.yaml").exists()
    assert "status=ready" in result.stdout


def test_validate_rejects_missing_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "missing"
    workspace.mkdir()

    result = run_cli("validate", str(workspace))

    assert result.returncode == 1
    assert "Missing artifacts" in result.stderr
