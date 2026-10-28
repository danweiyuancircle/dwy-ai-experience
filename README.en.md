# dwy-ai-experience

A public source monorepo for shared libraries and development tools, with public npm/PyPI packages, organized into CLI, backend, frontend, and Apple client code.

[中文](README.md) · [Documentation](docs/README.md) · [Source and package distribution](docs/private-distribution.md)

## Layout

| Path | Package / purpose |
| --- | --- |
| `dwy-cli/` | `create-dwy`: CLI, project scaffolding, and AI configuration sync |
| `dwy-cli/templates/ai-tools/` | Distributable skills, rules, hooks, and hook manifests |
| `dwy-cli/templates/project/` | Project scaffolding templates |
| `backend/src/dwyeapi/` | `dwyeapi`: FastAPI infrastructure |
| `backend/packages/device-fingerprint/` | `dwy-device-fingerprint`: standalone device identity |
| `backend/packages/auth/` | `dwy-auth`: application authentication and separate admin sessions |
| `frontend/eui/` | `@dwydev/eui`: Vue components |
| `frontend/ekit/` | `@dwydev/ekit`: frontend utilities |
| `frontend/admin-shell/` | `@dwydev/admin-kit`: administrator application framework |
| `frontend/auth-web/` | `@dwydev/auth-web`: Web authentication and Cookie sessions |
| `frontend/playground/` | Documentation and component demos |
| `ios/` | AppleAppKit: iOS/macOS frameworks, authentication, tests, and templates |
| `ci/`, `scripts/`, `.github/` | Shared validation and build/release tooling |

The root `Package.swift` provides the remote SwiftPM entry point; implementation and tests live under `ios/`. The root `package.json`, `pnpm-workspace.yaml`, and `pnpm-lock.yaml` manage the CLI and frontend packages. Python packages use uv separately.

The root `.claude/` and `.agents/` configure development of this repository; distributable AI templates belong to `dwy-cli/templates/ai-tools/`.

## Development

Use the Node version in `.node-version` and the pnpm version declared in the root `package.json`. Run from the repository root:

```bash
pnpm install --frozen-lockfile
uv sync --project ci --frozen

pnpm build:frontend
pnpm --dir frontend/auth-web build
pnpm --dir frontend/playground dev
node dwy-cli/bin/index.js --help
```

The locked Python development environment under `ci/` references the local EAPI, application authentication, and device fingerprint packages.

## Validation

```bash
uv run --project ci --frozen pytest backend/tests backend/packages/auth/tests scripts/tests -q -o asyncio_mode=auto
pnpm --dir frontend/eui test
pnpm --dir frontend/ekit test
pnpm --dir frontend/admin-shell test
pnpm --dir frontend/auth-web test
pnpm --dir dwy-cli test
swift test
```

Apple validation requires a full Xcode installation. For local Node 26 Vitest/jsdom Web Storage compatibility, see [docs/private-distribution.md](docs/private-distribution.md).

## Integration and distribution

- Authentication overview: [docs/auth.md](docs/auth.md).
- EUI integration/design and Tasks guides: [docs/README.md](docs/README.md).
- Apple frameworks and examples: [ios/README.md](ios/README.md).
- Public source and package installation: [docs/private-distribution.md](docs/private-distribution.md).

GitHub source is public; npm/PyPI packages are public and available for anyone to install. Package tags trigger `.github/workflows/publish-*.yml` using OIDC. `dwy upgrade` updates from public npm, and bundled CLI templates do not require repository access. SwiftPM continues to use semantic tags in the same Git repository. Cross-package CI and optional GitHub snapshots remain in `.github/workflows/private-release.yml`.

Historical migration, release, and consumer verification evidence lives in [docs/archive/README.md](docs/archive/README.md); it is not the current integration guide.
