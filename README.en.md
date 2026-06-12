# dwy-ai-experience

> dwy-ai-experience is an AI-focused engineering repository that combines frontend libraries, a CLI scaffolding workflow, and backend templates.

[中文](./README.md)

## Table of Contents

- [Overview](#overview)
- [Repository structure](#repository-structure)
- [Core features of claude-cli](#core-features-of-claude-cli)
- [Getting started](#getting-started)
- [Development](#development)
- [Release and versioning](#release-and-versioning)
- [Contributing](#contributing)
- [License](#license)

## Overview

`dwy-ai-experience` is a monorepo for AI engineering practices:

- Frontend libraries: `frontend/eui`, `frontend/ekit`
- Scaffolding and sync tooling: `claude-cli`
- Backend service: `backend` (FastAPI)

## Repository structure

- `/backend`: backend service and runtime
- `/frontend/eui`: Vue component library
- `/frontend/ekit`: Vue utility library
- `/frontend/playground`: component playground
- `/claude-cli`: scaffold and rules sync tool

## Core features of claude-cli

`claude-cli` is the central automation tool:

- Project scaffolding
  - `dwy create <project-name>`: generate standard project templates
- Rules and skill synchronization
  - `dwy sync`: sync selected conventions into the workspace
  - `dwy claude sync`: sync skills/rules/hooks into `.claude/`
  - `dwy claude sync md`: sync project `CLAUDE.md` into global config
  - `dwy codex sync`: convert Claude templates and sync into `.agents/` and `.codex/hooks/`
- Release governance
  - Standardized npm/PyPI release flow with GitHub Action OIDC
- Platform and adaptation rules
  - Common constraints for mobile full-screen adaptation, icon library usage, and annotation requirements

## Getting started

### Install

```bash
cd claude-cli
pnpm install
```

### Run

```bash
npx create-dwy your-project

dwy sync
dwy claude sync
dwy codex sync
```

## Development

```bash
cd frontend/eui && pnpm install && pnpm build
cd frontend/ekit && pnpm install && pnpm build
cd backend && uv sync
```

## Release and versioning

### CLI

- Trigger: push `create-dwy@x.y.z` tag
- Pipeline: GitHub Actions with OIDC (no committed publish secrets)
- Result: npm publish and GitHub Release auto-created

### Frontend packages

- eui and ekit follow a unified build and publish flow.

## Contributing

- Follow repository conventions in `AGENTS.md`
- Keep scoped commits per package when possible
- If you update shared templates or rules, sync corresponding paths under `claude-cli/templates/`

## License

MIT
