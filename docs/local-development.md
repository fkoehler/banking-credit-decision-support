# Local development

The default runtime is native: Java, Python, Node and PostgreSQL run as local
processes. Docker is not required.

## Prerequisites

- macOS or Linux shell with `bash`
- [SDKMAN](https://sdkman.io/) and [direnv](https://direnv.net/)
- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node.js 22 or later and pnpm
- PostgreSQL with the `vector` extension

The Maven Wrapper is committed, so a global Maven installation is not required.

On macOS, Homebrew can provide the non-Java prerequisites. Formula availability
can change; inspect `brew info postgresql pgvector` before choosing a PostgreSQL
major version. The `vector.control` file must belong to the active `pg_config`:

```bash
pg_config --version
ls "$(pg_config --sharedir)/extension/vector.control"
```

## First start

```bash
sdk env install
direnv allow
./dev doctor
./dev bootstrap
./dev up
./dev seed
```

Open <http://localhost:5173>. `bootstrap` downloads project dependencies and the
local embedding model, creates the configured database when necessary, enables
`vector`, and trains the synthetic risk model. It never installs system packages.

## Day-to-day commands

| Command | Purpose |
|---|---|
| `./dev doctor` | Verify the local toolchain and matching pgvector installation |
| `./dev bootstrap` | Resolve dependencies, initialize storage and train the model |
| `./dev up` | Start the three application processes and write `.run/logs` |
| `./dev seed` | Idempotently index fictional policies and create a sample case |
| `./dev test` | Run Java, Python, frontend and infrastructure checks |
| `./dev down` | Stop only PIDs recorded by this repository |

Follow startup logs with:

```bash
tail -f .run/logs/*.log
```

## Personal configuration

`.envrc` contains safe defaults. Put any override or secret in `.envrc.local`,
then run `direnv allow` again. That file is gitignored. See
[Configuration](configuration.md) for the complete mapping.

## Troubleshooting

### Java is not 21

```bash
sdk env install
sdk env
java -version
```

### PostgreSQL is not ready

Start the service supplied by your PostgreSQL installation and verify it with
`pg_isready`. `./dev` will not start or stop a system database service.

### pgvector is missing

The extension must be compiled for the same PostgreSQL reported by `pg_config`.
Reinstall the matching packages or select the correct PostgreSQL `bin` directory,
then confirm that `vector.control` exists before running bootstrap again.

### Reset demo data

Stop the application and drop only the dedicated `bank_credit_support` database,
then run `./dev bootstrap` and `./dev seed`. Confirm the database name before any
drop operation; the repository intentionally does not automate destructive reset.

