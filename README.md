# Public Training: Data Demand Agent

This repository is a public-safe training project that demonstrates how a data demand
agent can be designed, implemented, validated, and rolled out.

It is intentionally **not** a copy of an internal production repository. All domains,
tables, SQL, data, and examples are synthetic.

## What This Teaches

- How to turn a vague data request into structured requirement artifacts.
- How to inspect table metadata and lineage before writing SQL.
- How to generate and validate a delivery plan with gates.
- How to preserve evidence without exposing sensitive production data.
- How to build a small CLI that enforces the workflow.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
demo-demand-agent --help
pytest -q
```

## Demo Flow

```bash
demo-demand-agent demand new examples/requests/refund_metrics.json
demo-demand-agent metadata tables
demo-demand-agent metadata lineage mart.refund_metrics_daily
demo-demand-agent validate examples/workspaces/refund_metrics
```

The generated artifacts are written under `examples/workspaces/`.
The implementation uses only the Python standard library at runtime.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/demo_demand_agent/` | Small public-safe CLI implementation |
| `data/` | Synthetic catalog, lineage, and sample rows |
| `examples/requests/` | Synthetic demand requests |
| `examples/workspaces/` | Generated demo artifacts |
| `docs/` | Training material and rollout guide |
| `tests/` | Unit tests for the training CLI |

## Public Safety Rules

- No real company names, internal domains, private table names, IPs, tokens, cookies, or user data.
- No production SQL or query result samples.
- No screenshots, logs, or config files from real environments.
- Evidence examples use counts, schemas, hashes, and synthetic rows only.
