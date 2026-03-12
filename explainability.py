"""
explainability.py
Feature-importance based model explanations.

Takes a dict of feature scores and a prediction value, and returns
a ranked explanation of which factors drove the prediction.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FeatureContribution:
    """A single feature's contribution to the prediction."""

    name: str
    score: float
    weight: float
    contribution: float  # score × weight
    direction: str  # "increasing" or "decreasing"


@dataclass
class ModelExplanation:
    """Structured explanation for a model prediction."""

    prediction: float
    factors: List[FeatureContribution]
    top_driver: str
    narrative: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def model_explain(
    features: Dict[str, float],
    prediction: float,
    *,
    weights: Optional[Dict[str, float]] = None,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """Explain why a model produced a given prediction.

    Parameters
    ----------
    features : dict
        Mapping of ``{feature_name: raw_score}`` (0–1 scale).
    prediction : float
        The final prediction / risk score.
    weights : dict, optional
        Mapping of ``{feature_name: weight}``.  If *None*, features are
        weighted equally.
    threshold : float
        The decision threshold that separates low from high risk.

    Returns
    -------
    dict
        :class:`ModelExplanation` serialised to a dictionary.
    """
    if not features:
        return ModelExplanation(
            prediction=prediction,
            factors=[],
            top_driver="N/A",
            narrative="No features provided for explanation.",
        ).to_dict()

    # Default to equal weights when none supplied
    if weights is None:
        equal_w = 1.0 / len(features)
        weights = {name: equal_w for name in features}

    contributions: List[FeatureContribution] = []
    for name, score in features.items():
        w = weights.get(name, 0.0)
        contrib = score * w
        contributions.append(
            FeatureContribution(
                name=name,
                score=round(score, 4),
                weight=round(w, 4),
                contribution=round(contrib, 4),
                direction="increasing" if score >= threshold else "decreasing",
            )
        )

    # Sort by absolute contribution descending
    contributions.sort(key=lambda c: abs(c.contribution), reverse=True)

    top = contributions[0]

    # Build human-readable narrative
    above_threshold = [c for c in contributions if c.direction == "increasing"]
    narrative_parts: List[str] = []
    if prediction >= threshold:
        narrative_parts.append(
            f"The prediction ({prediction:.2f}) is ABOVE the threshold ({threshold:.2f})."
        )
    else:
        narrative_parts.append(
            f"The prediction ({prediction:.2f}) is below the threshold ({threshold:.2f})."
        )

    narrative_parts.append(
        f"The top driver is '{top.name}' (contribution {top.contribution:.3f})."
    )

    if above_threshold:
        names = ", ".join(c.name for c in above_threshold[:3])
        narrative_parts.append(f"Risk-increasing factors: {names}.")

    explanation = ModelExplanation(
        prediction=round(prediction, 4),
        factors=contributions,
        top_driver=top.name,
        narrative=" ".join(narrative_parts),
    )

    logger.debug("Explanation generated for prediction=%.4f, top_driver=%s", prediction, top.name)
    return explanation.to_dict()


if __name__ == "__main__":
    # Quick demo
    result = model_explain(
        features={"volatility": 0.8, "sentiment": 0.3, "governance": 0.6, "technical": 0.5},
        prediction=0.62,
        weights={"volatility": 0.4, "sentiment": 0.3, "governance": 0.2, "technical": 0.1},
    )
    print(f"Prediction: {result['prediction']}")
    print(f"Top driver: {result['top_driver']}")
    print(f"Narrative:  {result['narrative']}")
    print("Factors:")
    for f in result["factors"]:
        print(f"  {f['name']:>12}: score={f['score']:.2f}  weight={f['weight']:.2f}  contribution={f['contribution']:.3f}  ({f['direction']})")
