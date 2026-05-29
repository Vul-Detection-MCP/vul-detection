from typing import List

from thefuzz import fuzz

from entity.evaluation_result import EvaluationResult
from entity.result import Result


def convert_response_to_int(content: str) -> int:
    ratio = fuzz.ratio(content.lower(), "yes")
    if ratio < 20:
        return 0
    return 1


def precision(true_positives: int, false_positives: int) -> float:
    return true_positives / (true_positives + false_positives)


def recall(true_positives: int, true_negatives: int) -> float:
    return true_positives / (true_positives + true_negatives)


def get_results(responses: List[Result]) -> EvaluationResult:
    true_positive = len([r for r in responses if r.target == r.actual])
    false_positive = len([r for r in responses if r.target == 0 and r.actual == 1])
    true_negative = len([r for r in responses if r.target == 1 and r.actual == 0])

    return EvaluationResult(
        precision(true_positive, false_positive), recall(true_positive, true_negative)
    )

if __name__ == '__main__':
    print("")
