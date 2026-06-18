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
    total_pairs = total_rows / 2

    tp = ((data["target"] == 1) & (data["actual"] == 1)).sum()
    fp = ((data["target"] == 0) & (data["actual"] == 1)).sum()
    fn = ((data["target"] == 1) & (data["actual"] == 0)).sum()

    precision = evaluation_service.precision(tp, fp)
    recall = evaluation_service.recall(tp, fn)
    f1 = 0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)

    data["pair_id"] = data.index // 2
    pairs = data.groupby("pair_id").apply(
        lambda g: {
            "t0": g.iloc[0]["target"],
            "t1": g.iloc[1]["target"],
            "a0": g.iloc[0]["actual"],
            "a1": g.iloc[1]["actual"],
            "c0": g.iloc[0]["target"] == g.iloc[0]["actual"],
            "c1": g.iloc[1]["target"] == g.iloc[1]["actual"],
        }
    ).apply(pd.Series)

    pair_wise_correct = ((pairs["c0"]) & (pairs["c1"])).sum()
    pair_wise_both_vulnerable = ((pairs["a0"] == 1) & (pairs["a1"] == 1)).sum()
    pair_wise_both_benign = ((pairs["a0"] == 0) & (pairs["a1"] == 0)).sum()
    pair_wise_reversed = ((pairs["a0"] == pairs["t1"]) & (pairs["a1"] == pairs["t0"])).sum()

    summary = pd.DataFrame([
        ["Total rows", total_rows],
        ["Correct rows", correct_rows],
        ["Accuracy", round(correct_rows / total_rows, 2)],
        ["Precision", round(precision, 2)],
        ["Recall", round(recall, 2)],
        ["F1", round(f1, 2)],
        ["Pair-wise both correct", f"{pair_wise_correct} ({pair_wise_correct / total_pairs:.2%})"],
        ["Pair-wise both vulnerable", f"{pair_wise_both_vulnerable} ({pair_wise_both_vulnerable / total_pairs:.2%})"],
        ["Pair-wise both benign", f"{pair_wise_both_benign} ({pair_wise_both_benign / total_pairs:.2%})"],
        ["Pair-wise reversed", f"{pair_wise_reversed} ({pair_wise_reversed / total_pairs:.2%})"],
    ], columns=["Metric", "Value"])

    print("File:", str(results_file))
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
