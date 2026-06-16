import sys

import evaluation_service
import pandas as pd


def main():
    if len(sys.argv) < 2:
        print("Usage: script.py <CSV results>")
        return

    results_file = sys.argv[1]
    data = pd.read_csv(results_file)

    correct_rows = (data["target"] == data["actual"]).sum()
    total_rows = len(data)

    tp = ((data["target"] == 1) & (data["actual"] == 1)).sum()
    fp = ((data["target"] == 0) & (data["actual"] == 1)).sum()
    fn = ((data["target"] == 1) & (data["actual"] == 0)).sum()

    precision = evaluation_service.precision(tp, fp)
    recall = evaluation_service.recall(tp, fn)

    data["correct"] = data["target"] == data["actual"]
    correct_pairs = (data.groupby(data.index // 2)["correct"]
        .all()
        .sum()
     )

    summary = pd.DataFrame([
        ["Total rows", total_rows],
        ["Correct rows", correct_rows],
        ["Accuracy", round(correct_rows / total_rows, 2)],
        ["Precision", round(precision, 2)],
        ["Recall", round(recall, 2)],
        ["Correct pairs", correct_pairs],
    ], columns=["Metric", "Value"])

    print("File:", str(results_file))
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
