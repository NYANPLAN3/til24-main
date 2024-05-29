# py-api-template

Template for FastAPI-based API server. Features:

- Supports both CPU/GPU-accelerated setups automatically.
- Poetry for package management.
- Ruff for formatting & linting.
- VSCode debugging tasks.
- Other QoL packages.

Oh yeah, this template should work with the fancy "Dev Containers: Clone Repository
in Container Volume..." feature.

## Usage Instructions

- Replace all instances of `py-api-template`. Optionally, rename `src` to a nicer name.
  - Tip: Rename the `src` folder first for auto-refactoring.

## Useful Commands

Ensure the virtual environment is active and `poetry install` has been run before using the below:

```sh
# Launch debugging server, use VSCode's debug task instead by pressing F5.
poe dev
# Run any tests.
poe test
# Build docker image for deployment; will also be tagged as latest.
poe build {insert_version_like_0.1.0}
# Run the latest image locally.
poe prod
# Publish the latest image.
poe publish
```
