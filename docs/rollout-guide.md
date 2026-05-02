# Rollout Guide

This demo maps a production-grade data demand workflow into a public-safe
training repository.

## Production Concept to Demo Mapping

| Production Concept | Public Demo Equivalent |
| --- | --- |
| Internal metadata catalog | `data/catalog.json` |
| Internal lineage service | `data/lineage.json` |
| Demand workspace | `examples/workspaces/<demand>/` |
| Query evidence | `evidence.yaml` with synthetic-only policy |
| Stage gates | `demo-demand-agent validate` |

## Public-Safe Evidence Pattern

Use this pattern for public training:

- Save schemas, row counts, null rates, and hashes.
- Use synthetic rows when row-level examples are needed.
- Avoid real table names, internal domains, task IDs, logs, tickets, and user data.
- Keep credentials outside the repository.

## Suggested Live Demo

```bash
demo-demand-agent demand new examples/requests/refund_metrics.json
demo-demand-agent metadata schema mart.refund_metrics_daily
demo-demand-agent metadata lineage mart.refund_metrics_daily
demo-demand-agent validate examples/workspaces/refund_metrics
```
