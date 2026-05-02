# Training Outline

## Audience

Data engineers, analytics engineers, and technical program managers who want to
understand how an agentic workflow can make data demand delivery more reliable.

## Session Plan

1. Start from an ambiguous request.
2. Convert it into required fields and a demand workspace.
3. Inspect synthetic metadata and lineage.
4. Write an analysis plan before SQL implementation.
5. Validate evidence and status artifacts.
6. Discuss rollout controls: reviews, gates, and public-safe evidence.

## Key Design Ideas

- Separate requirement capture from implementation.
- Make metadata checks explicit and repeatable.
- Treat evidence as a first-class artifact.
- Store aggregate proof and synthetic samples instead of sensitive raw rows.
- Keep gates small enough to run locally.
