# CHANGELOG.md

## v0.4.0

### Features
- Functional `explainability.py` — ranked feature-importance explanations with narratives
- Rich `mock_mode.py` — seed-controlled generators for events, risk assessments, volatility

### API & Documentation
- Expanded `openapi.yaml` — 5 endpoints with full request/response schemas
- Structured logging in `alerts.py` (replaced all `print()` with `logging`)

### Testing
- 14-test suite for scenario simulator (upgrade types, market conditions, weights, edge cases)

## v0.3.0

### Validation & Quality
- Upgraded `validation.py` with Pydantic `BlockchainEvent` and `AlertRequest` models
- Field constraints, chain/event-type validators, strict validation mode
- Added `pydantic>=2.0.0` dependency

### Testing
- 30-test unit test suite for `RiskAssessment` scoring logic
- Tests cover volatility/sentiment normalization, risk categorization, recommendations, protocol comparison

### Features
- Functional `scenario_simulator.py` with composite risk scoring
  - 4 weighted factors: volatility, sentiment, governance, technical
  - Lookup tables for upgrade types, market conditions, chain complexity
  - Structured output with risk breakdown and recommendations

### Infrastructure
- Removed deprecated `version` key from `docker-compose.yaml`
- Added healthchecks to postgres (`pg_isready`) and redis (`redis-cli ping`)
- Condition-based `depends_on` for proper service startup ordering

### Documentation
- Added `CONTRIBUTING.md` with dev setup, testing, linting, PR guidelines

## v0.2.0

### Improvements
- Exponential backoff and robust error handling for Snapshot & Tally API clients
- Tally API key authentication support via `TALLY_API_KEY` env variable
- Cross-chain event correlation engine with time-window clustering and confidence scoring
- WebSocket server: env-configurable CORS origins, safe connection cleanup
- DEMO_MODE support in config validation (run without API keys)

### Infrastructure
- Added `__init__.py` files for proper Python package structure
- Added `pyproject.toml` with project metadata, pytest, and ruff config
- Added multi-stage `Dockerfile` with non-root user and healthcheck
- Added `.dockerignore` for lean build contexts
- Added GitHub Actions CI pipeline (ruff lint + pytest)

### Testing
- Shared pytest fixtures in `tests/conftest.py`
- 10-test suite for cross-chain analytics correlation engine

### Documentation
- macOS installation notes for Torch and Prophet
- Environment variable reference in README

## v0.1.0 (MVP)
- Real-time alerting stubs added
- Auto-mitigation hooks stubbed
- Security best-practices and secret management
- Modular microservices docker-compose
- Model explainability stub (SHAP/feature importance)
- User-driven risk model factors
- Scenario simulation stub script
- Advanced analytics (cross-chain, alpha signals) stubs
- Developer tooling: one-click setup, API mocks, minimum test coverage
- Swagger/OpenAPI spec for API

### Known Issues
- No real email/slack/webhook integration yet (use stubs)
- Scenario simulation and explainability are placeholders
- No production DDOS/rate-limiter code
- Intended for demo/MVP use—harden before production

