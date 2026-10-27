# Local setup notes

Notes on the changes made so the project runs on this machine (Intel Mac,
Homebrew uv 0.11.26).

## The problem

Running uv in the project failed with:

```
Required uv version `>=0.13.5` does not match the running version `0.11.26`
```

## What we tried first

- `brew upgrade uv` to get uv 0.13.6. Homebrew had no prebuilt package for
  this Mac, so it started compiling uv and its toolchain (openssl, LLVM,
  Rust) from source. That would have taken hours, so we stopped it and ran
  `brew link uv` to restore the old uv.
- Lowering only the uv version requirement was not enough. The project also
  required Python `>=3.13.17`, and uv 0.11.26 can only install Python up to
  3.13.14:

  ```
  error: No interpreter found for Python >=3.13.17, <3.14
  ```

## What made it work

We loosened the version pins to match what is available locally:

| File                            | Setting            | Before             | After              |
| ------------------------------- | ------------------ | ------------------ | ------------------ |
| `pyproject.toml`                | `required-version` | `>=0.13.5`         | `>=0.11`           |
| `pyproject.toml`                | `requires-python`  | `>=3.13.17`        | `>=3.13.14`        |
| `.python-version`               | Python pin         | `>=3.13.17,<3.14`  | `>=3.13.14,<3.14`  |
| `bonus_solution/pyproject.toml` | `required-version` | `>=0.13.5`         | `>=0.11`           |
| `uv.lock`                       | `requires-python`  | `>=3.13.17`        | `>=3.13.14`        |

Then:

```sh
uv lock   # regenerated the lockfile; every package version stayed the same
uv sync   # created .venv with Python 3.13.14
```

All runtime dependencies (matplotlib, pandas, plotly, scikit-learn, seaborn,
skops) import correctly.

`bonus_solution` still requires Python 3.13.17 because it runs in Docker
(`python:3.13.17-slim-bookworm`), which does not depend on the local Python.

## Caveats

- The environment runs Python 3.13.14, a few patch releases below what the
  project asks for. That's fine for this work, but it differs from the
  original setup.
- These are local changes. Don't push them unless the rest of the team
  agrees.

## Going back to the original setup

1. Install a current uv with Astral's installer, which downloads a prebuilt
   binary in seconds:
   `curl -LsSf https://astral.sh/uv/install.sh | sh`, then `brew uninstall uv`.
2. Revert the pins with
   `git checkout -- pyproject.toml .python-version uv.lock bonus_solution/pyproject.toml`.
3. Run `uv sync`.


Run pipeline: uv run python -m src.data_pipeline