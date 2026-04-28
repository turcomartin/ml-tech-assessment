# ml-tech-assessment

## Environment Setup

> **Note on tooling — `uv` vs Conda**
>
> The instructions below use Conda for environment management, but [`uv`](https://github.com/astral-sh/uv) is worth considering for a Python-only project like this one. Conda is designed for polyglot scientific stacks (Python + R + native libs); here everything is pure Python, so Conda's extra weight (slow solver, `libmamba` dependency, multi-hundred-MB base install) adds friction without benefit. `uv` creates and manages virtual environments in milliseconds, resolves and installs dependencies significantly faster than pip or Poetry alone, and works directly with `pyproject.toml`. If you prefer a lighter setup:
>
> ```bash
> # install uv (once)
> curl -LsSf https://astral.sh/uv/install.sh | sh
>
> # create venv + install all deps in one step
> uv sync
>
> # run any command inside the venv
> uv run uvicorn solution.server.main:app --reload
> uv run pytest
> ```
>
> The Conda + Poetry path below remains fully supported.

### Using Conda (Recommended)

1. Install Conda if you haven't already:
   - Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution)

2. Create and activate a new conda environment:
   ```bash
   conda create -n ml-assessment python=3.12
   conda activate ml-assessment
   ```

## Installing Poetry and Dependencies

1. Install Poetry using pip:
   ```bash
   pip install poetry
   ```

2. Install project dependencies:
   ```bash
   poetry install
   ```

## Environment Variables

> **Required before starting the server.** Copy the example and fill in your values:

```bash
cp ".env copy.example" .env
```

Then edit `.env` in the repo root:

```env
OPENAI_API_KEY=sk-...             # required for real calls; leave blank when MOCK_LLM=true
OPENAI_MODEL=gpt-4o-2024-08-06   # optional, this is the default
MOCK_LLM=false                    # set to true to skip real API calls
```

The server validates this file at startup and will exit immediately with a clear error if it is missing or misconfigured.

## Running Tests

To run the tests, make sure you have:
1. Activated your virtual environment
2. Installed all dependencies using Poetry
3. Created and populated the `.env` file

Then run:
```bash
pytest
```

For more detailed test output:
```bash
pytest -v
```

For test coverage report:
```bash
pytest --cov
```
