# MODEL_LIFECYCLE.md

## Model Lifecycle Management

- **Retrain Schedule:** Document the frequency of retraining (e.g., every 2 weeks or after critical upgrade events).
- **Validation:** Specify test datasets. Log validation metrics after each retrain.
- **Versioning:** Use DVC or similar tool for model/data versioning. Tag each major model with metadata (date, version, metrics).
- **Rollback Policy:** Keep the previous N model versions and support rollback on performance regression.

_Replace with real policies and triggers as you grow._

