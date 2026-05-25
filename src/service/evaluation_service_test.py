import math

from service import evaluation_service


def test_precision():
    true_positives = 4
    false_positives = 6

    actual = evaluation_service.precision(true_positives, false_positives)

    assert math.isclose(actual, 0.4)


def test_recall():
    true_positives = 2
    true_negatives = 8

    actual = evaluation_service.precision(true_positives, true_negatives)

    assert math.isclose(actual, 0.2)
