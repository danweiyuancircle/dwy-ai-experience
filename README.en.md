<div align="center">
  <h1>dwy-ai-experience</h1>
  <p><strong>Personal AI engineering repository by dwy</strong></p>
  <p>Focused on AI tooling, project scaffolding, rules sync, and release automation</p>
  <p>
    <a href="./README.md">中文</a>
  </p>
  <p>
    <a href="https://github.com/danweiyuancircle/dwy-ai-experience/actions/workflows/private-release.yml">Private builds and releases</a>
    <img src="https://img.shields.io/github/license/danweiyuancircle/dwy-ai-experience" alt="license" />
    <img src="https://img.shields.io/badge/platform-Claude%20%2F%20Codex-blue" alt="platform" />
  </p>
</div>

## Overview

This repository is now private. All iOS/macOS frameworks, Google sign-in clients, tests, and templates live in `ios/`; backend and Web authentication modules live in `modules/auth/`. The root `Package.swift` remains the remote SwiftPM entry point, with every target under `ios/`. New packages are distributed through authenticated private GitHub Releases. Public npm/PyPI examples below apply to historical public versions; see [the private distribution guide](docs/private-distribution.md) for current installation.

`dwy-ai-experience` is a monorepo built around AI development workflows. It currently brings together three major areas:

- `dwy-cli`: scaffolding, rule templates, and Claude/Codex sync entrypoint
- `frontend/*`: UI libraries, utility libraries, and playground
- `backend`: FastAPI backend foundation and service templates

The focus of this repository is not a single package. It is a reusable toolchain that standardizes project bootstrap, AI coding constraints, shared rules, and release workflow.

## Core Packages

### `@dwydev/eui`

Vue 3 component library built with shadcn UI visual style, Element UI-style API usage, Tailwind CSS 4, and Reka UI, designed for admin panels, dashboards, business forms, and internal tools.

```bash
npm install @dwydev/eui
```

### `dwyeapi`

Infrastructure library for FastAPI projects, covering config, exceptions, database, security, cache, pagination, logging, and other shared backend capabilities.

```bash
pip install dwyeapi
```

### `@dwydev/ekit`

Vue 3 utility library that provides hooks, request wrappers, time utilities, download helpers, cookies, querystring handling, and other shared project utilities.

```bash
npm install @dwydev/ekit
```

## Highlights

- Unified project bootstrap, rules distribution, skill sync, and hooks sync
- Supports both `Claude` and `Codex` local collaboration setup
- Swift, Python and npm packages validated and distributed through private GitHub Actions releases
- Shared engineering rules for mobile full-screen adaptation, icon libraries, and code annotation

## Claude CLI

`dwy-cli` is the core module in this repository. It does more than scaffolding: it turns team conventions into executable tooling.

### Core Commands

- `dwy create <project-name>`
  - Generate a standard project template
- `dwy` / `dwy sync`
  - Choose an action: sync global skills, or sync selected rules / skills / hooks into the current project
- `dwy upgrade`
  - Upgrade the global `create-dwy` install to npm latest

### What It Solves

- Bootstraps new projects with a standard structure and base engineering setup
- Eliminates manual copy-paste for team conventions
- Keeps Claude Code and Codex project-level configuration in sync
- Pushes release flow toward auditable GitHub Actions automation

## Repository Structure

- `/dwy-cli`
  - `create-dwy` CLI, sync logic, templates, and rule sources
- `/frontend/eui`
  - Vue component library
- `/frontend/ekit`
  - Vue utility library
- `/frontend/playground`
  - Component playground and docs site
- `/backend`
  - FastAPI infrastructure and backend templates

## Libraries

### `@dwydev/eui`

Vue 3 component library built with shadcn UI visual style, Element UI-style API usage, Tailwind CSS 4, and Reka UI.

- Core components: buttons, inputs, popovers, menus, tables, calendars
- Style and API: shadcn UI styling + Element UI usage pattern
- Foundation: Tailwind CSS 4 + Reka UI
- Typical use cases: admin panels, dashboards, internal tools, business forms

```bash
npm install @dwydev/eui
```

### `@dwydev/ekit`

Vue 3 utility library that provides common hooks, request wrappers, time utilities, download helpers, cookies, and other shared project utilities.

- Common hooks and helper functions
- Request-layer plugin chain
- File download, cookies, querystring, and related utilities

```bash
npm install @dwydev/ekit
```

### `dwyeapi`

FastAPI infrastructure library for backend projects, covering config, exceptions, database, security, cache, pagination, and logging.

- Config management with `pydantic-settings`
- Database support with `SQLAlchemy asyncio`
- Security utilities: JWT and password hashing
- Infrastructure: Redis, pagination, logging, unified exception handling

```bash
pip install dwyeapi
```

For task queue or email extras:

```bash
pip install "dwyeapi[tasks]"
pip install "dwyeapi[email]"
```

## Quick Start

### Install CLI Dependencies

```bash
cd dwy-cli
pnpm install
```

### Create And Sync

```bash
npx create-dwy your-project

dwy sync
```

## Development

```bash
cd frontend/eui && pnpm install && pnpm build
cd frontend/ekit && pnpm install && pnpm build
cd backend && uv sync
```

## Release

`.github/workflows/private-release.yml` validates branches and publishes semantic tags (starting with `0.4.1`) to private GitHub Releases. SwiftPM uses the same Git tag; Web/Python packages use tgz/wheel/sdist assets with SHA256 manifests. Legacy public workflows are disabled. See [the distribution guide](docs/private-distribution.md).

See the [migration acceptance report](docs/migration-reports/acceptance.md) for module boundaries, the published release, and consumer verification.

## Contributing

- Follow repository conventions in [`AGENTS.md`](./AGENTS.md)
- Keep cross-package changes scoped and explicit
- If you update shared templates or rules, sync `dwy-cli/templates/` as well

## License

MIT
