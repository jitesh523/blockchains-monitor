# Contributing to Blockchain Protocol Upgrade Monitor

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. **Clone and set up the environment**
   ```bash
   git clone https://github.com/jitesh523/blockchains-monitor.git
   cd blockchains-monitor
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys, or set DEMO_MODE=true
   ```

3. **Install dev tools**
   ```bash
   pip install pytest ruff
   ```

## Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run a specific test file
python3 -m pytest tests/test_risk_model.py -v

# Run with short tracebacks
python3 -m pytest tests/ -v --tb=short
```

## Linting

We use [Ruff](https://docs.astral.sh/ruff/) for linting. Configuration is in `pyproject.toml`.

```bash
# Check for lint errors
ruff check .

# Auto-fix what's possible
ruff check . --fix
```

## Project Structure

```
├── app.py                   # Streamlit app entry point
├── production_app.py        # Production app with monitoring
├── config/                  # Configuration module
├── src/
│   ├── api/                 # API clients (governance, blockchain)
│   ├── models/              # ML models (volatility, sentiment, risk)
│   ├── services/            # Backend services (cache, DB, monitoring)
│   ├── ui/                  # Streamlit UI components
│   └── utils/               # Shared utilities
├── tests/                   # Pytest test suite
├── Dockerfile               # Container build
├── docker-compose.yaml      # Multi-service deployment
└── pyproject.toml           # Project config and tool settings
```

## Pull Request Guidelines

1. **Branch from `main`** — create a feature branch (e.g. `feat/my-feature`)
2. **Write tests** — add or update tests in `tests/` for any new logic
3. **Lint before pushing** — ensure `ruff check .` passes
4. **Keep commits focused** — one logical change per commit
5. **Use conventional commit messages**:
   - `feat:` new features
   - `fix:` bug fixes
   - `test:` test additions/changes
   - `docs:` documentation
   - `chore:` maintenance / tooling
   - `build:` build/dependency changes

## Code Style

- **Python 3.11+** target
- **120 character** line length
- Use **type hints** for function signatures
- Use **logging** (not `print()`) in library code
- Use **Pydantic** models for input validation (see `validation.py`)

## Questions?

Open an issue on GitHub if you have questions or need help getting started.
