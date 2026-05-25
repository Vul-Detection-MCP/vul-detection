from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    precision: float
    recall: float
