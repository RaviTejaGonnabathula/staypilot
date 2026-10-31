# StayPilot

StayPilot is a multi-agent hotel services project for bookings, amenities, billing, and verified guest profile changes.

The planned application uses a FastAPI gateway and five Google ADK agents: Master, Booking, Amenities, Billing, and Profile. The repository groups them into separate Python packages so they can share common libraries while keeping their application responsibilities distinct.

## Current status

This repository currently contains the **project scaffold**:

- A Python 3.12 uv workspace with six application packages and five shared libraries.
- Valid package metadata, local package dependencies, and a generated `uv.lock`.
- Importable Python packages and stub modules for future application entrypoints.
- Directory placeholders for tests, migrations, fixtures, infrastructure, and deployment.
- Nonsecret configuration examples.

The gateway does not yet expose a FastAPI application, and the agent modules do not yet define `root_agent`. FastAPI, Google ADK, database libraries, and cloud SDKs have not been added as runtime dependencies. Authentication, business operations, tests, CI workflows, and cloud deployment are not implemented yet.

The intended cloud-test budget is **USD 5 per month**. Paid work that would exceed that limit is deferred; this scaffold does not implement spending controls.

## Repository structure

```text
staypilot/
|-- README.md
|-- pyproject.toml                 # Workspace definition and shared package sources
|-- uv.lock                        # Generated dependency lockfile
|-- .python-version                # Python 3.12
|-- .gitignore                     # Local environments, secrets, and generated files
|-- .env.example                   # Proposed local overrides; not loaded yet
|-- settings.dev.yaml              # Development configuration seed
|-- settings.qa.yaml               # QA configuration seed
|-- settings.prod.yaml             # Production configuration seed
|
|-- apps/
|   |-- gateway/
|   |   |-- pyproject.toml
|   |   `-- src/staypilot_gateway/
|   |       |-- __init__.py
|   |       |-- main.py             # Future FastAPI application entrypoint
|   |       |-- api/                # HTTP route implementations
|   |       |-- clients/            # Client for the remote Master agent
|   |       `-- static/             # Future HTML, CSS, and JavaScript portal
|   |
|   `-- agents/
|       |-- master/
|       |-- booking/
|       |-- amenities/
|       |-- billing/
|       `-- profile/
|
|-- packages/
|   |-- contracts/
|   |-- security/
|   |-- data/
|   |-- config/
|   `-- observability/
|
|-- migrations/
|   `-- versions/                  # Future database schema revisions
|-- data/
|   |-- seed/                      # Synthetic development fixtures
|   `-- eval/                      # Evaluation inputs and expected outcomes
|-- tests/
|   |-- unit/
|   |-- contracts/
|   |-- security/
|   |-- integration/
|   |-- eval/
|   `-- load/
|-- infra/
|   `-- gcp/                       # Future GCP provisioning definitions
|-- scripts/
|   `-- deploy/                    # Future packaging and deployment scripts
`-- .github/
    `-- workflows/                 # Reserved for GitHub Actions workflows
```

Directories that have no implementation yet contain a `.gitkeep` file so Git can retain them. In particular, `.github/workflows/` currently has no workflow YAML, and the test folders contain no tests.

The generated `.venv/` directory is local and ignored by Git. Original planning documents and conversation exports are kept outside this repository.

## Application packages

Each application has its own `pyproject.toml` and a uniquely named Python import package under `src/`.

| Application directory | Python import package | Intended responsibility |
|---|---|---|
| `apps/gateway/` | `staypilot_gateway` | Guest portal, API routes, login and sessions, explicit confirmations, TOTP verification, and calls to Master. |
| `apps/agents/master/` | `staypilot_master` | Understand requests, collect missing information, delegate to specialists, and compose responses. |
| `apps/agents/booking/` | `staypilot_booking` | Check availability, create reservations, and reschedule bookings. |
| `apps/agents/amenities/` | `staypilot_amenities` | Retrieve hotel facilities, branch information, and policies. |
| `apps/agents/billing/` | `staypilot_billing` | Read billing and folio information scoped to the authenticated guest. |
| `apps/agents/profile/` | `staypilot_profile` | Apply guest profile changes using operation-specific authorization. |

The Master package has this internal layout:

```text
apps/agents/master/
|-- pyproject.toml
`-- src/staypilot_master/
    |-- __init__.py
    |-- agent.py
    `-- transport/
        `-- __init__.py
```

`transport/` is reserved for authenticated remote calls to specialist agents. Master has no dependency on `staypilot-data` and should not perform business database operations.

The four specialist packages follow the same pattern. For example:

```text
apps/agents/booking/
|-- pyproject.toml
`-- src/staypilot_booking/
    |-- __init__.py
    |-- agent.py
    |-- tools/
    |   `-- __init__.py
    `-- services/
        `-- __init__.py
```

- **`agent.py`** will define the ADK agent, instructions, and available tools, exporting `root_agent` when implemented.
- **`tools/`** will contain the interfaces callable by the agent.
- **`services/`** will hold deterministic business rules, authorization checks, and transaction coordination.
- **`__init__.py`** identifies a Python package. These files currently contain descriptive docstrings.

For a future booking operation, the agent will call a tool, the tool will call a booking service, and that service will validate the request and use the shared database layer. The model's output must not substitute for authorization or transaction checks.

## Shared packages

Every shared library has its own `pyproject.toml` and `src/staypilot_<name>/__init__.py`.

| Directory | Python import package | Intended contents |
|---|---|---|
| `packages/contracts/` | `staypilot_contracts` | Request and response models, agent message contracts, and error types. |
| `packages/security/` | `staypilot_security` | Identity verification, authorization helpers, and approval validation. |
| `packages/data/` | `staypilot_data` | Database models, scoped repositories, and transaction helpers. |
| `packages/config/` | `staypilot_config` | Typed settings, environment selection, and configuration loading. |
| `packages/observability/` | `staypilot_observability` | Structured logging, trace correlation, and sensitive-data redaction. |

**`packages/data/` contains Python database code; root `data/` contains data files.** Store synthetic fixtures in `data/seed/` and evaluation cases in `data/eval/`.

Dependency boundaries:

- Gateway and specialists currently declare dependencies on all five shared libraries.
- Master declares dependencies on contracts, security, config, and observability only.
- The security and data packages depend on contracts. The other shared packages currently have no dependencies.
- Applications should communicate through their interfaces rather than importing another application's implementation.
- Shared libraries must not import application packages.
- Environment-specific database permissions and service identities still need implementation; folder boundaries alone do not enforce access control.

## Workspace and dependencies

The root [pyproject.toml](pyproject.toml) defines the workspace members:

```toml
[tool.uv.workspace]
members = ["apps/gateway", "apps/agents/*", "packages/*"]
```

Each member declares its dependencies in its own `pyproject.toml`. The root `tool.uv.sources` entries resolve shared StayPilot libraries from this workspace.

The root project is marked `package = false`; it organizes the workspace without supplying an additional importable application. There are **11 installable member packages** and one shared [uv.lock](uv.lock).

All projects require `>=3.12,<3.13`. Member packages use the pinned `uv_build==0.11.24` build backend. Generate lockfile changes through uv rather than editing the lockfile manually.

Separate packages provide the intended packaging boundaries for future independent deployments. Actual deployment bundles, remote invocation, and release workflows still need implementation.

See [uv's workspace documentation](https://docs.astral.sh/uv/concepts/projects/workspaces/) for workspace dependency and command behavior.

## Local setup on Windows

Install Git, uv, and Python 3.12. If Python 3.12 is missing, it can be installed with:

```powershell
uv python install 3.12
```

From the existing local checkout:

```powershell
Set-Location -LiteralPath 'R:\my_repos\staypilot'
uv sync --locked --all-packages --python 3.12
```

This creates or updates `.venv/` and installs all workspace member packages. Use `--all-packages` for commands that need multiple applications: a plain root-level `uv sync` or `uv run` selects the root project, whose dependency list is empty.

Check the interpreter and representative package imports:

```powershell
uv run --locked --all-packages python --version
uv run --locked --all-packages python -c "import staypilot_gateway, staypilot_master, staypilot_booking; print('Package imports OK')"
```

To work with one package and its declared dependencies:

```powershell
uv run --locked --package staypilot-booking python -c "import staypilot_booking; print('Booking package import OK')"
```

These commands verify package setup. They do not start the portal or invoke an agent; runnable application entrypoints have not been implemented.

## Configuration and supporting folders

The three `settings.*.yaml` files currently contain only an `environment` field. They do not provision environments, select databases, or configure cloud resources.

[.env.example](.env.example) proposes `STAYPILOT_ENV` and `STAYPILOT_SETTINGS_FILE` for the future settings loader. Neither these variables nor the YAML settings are consumed by the current stub modules. Keep real secret values out of tracked files; local `.env` files and `.secrets/` are ignored.

| Location | Intended use |
|---|---|
| `migrations/versions/` | Database schema changes under a future migration tool configuration. |
| `tests/unit/` | Focused deterministic service and helper checks. |
| `tests/contracts/` | Request, response, and cross-agent contract compatibility. |
| `tests/security/` | Ownership checks, authorization failures, approval binding, and replay prevention. |
| `tests/integration/` | Database and service interaction checks. |
| `tests/eval/` | Agent behavior checks using cases from `data/eval/`. |
| `tests/load/` | Controlled concurrency and performance checks. |
| `infra/gcp/` | Reproducible cloud resource provisioning. |
| `scripts/deploy/` | Package assembly, deployment, and release verification helpers. |
| `.github/workflows/` | Future CI and deployment automation. |

These supporting directories are placeholders. Their presence does not indicate that migrations, tests, infrastructure, or automation are operational.
