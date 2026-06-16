def convert_response_to_int(content: str) -> int:
    is_vulnerable = "yes" in content[:20].lower() or "yes" in content[-20:].lower()
    if is_vulnerable:
        return 1
    return 0


def convert_response_bool_to_int(content: str) -> int:
    is_vulnerable = "true" in content[:20].lower() or "true" in content[-20:].lower()
    if is_vulnerable:
        return 1
    return 0


def precision(true_positives: int, false_positives: int) -> float:
    return true_positives / (true_positives + false_positives)


def recall(true_positives: int, false_negatives: int) -> float:
    return true_positives / (true_positives + false_negatives)


if __name__ == '__main__':
    print("")
