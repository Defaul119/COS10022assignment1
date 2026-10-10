"""
Check what the reference workflow wrote after you click "Execute all" in KNIME.

KNIME writes its CSV Writer output into the workflow's data area:
    <KNIME workspace>/A1_Reference_Workflow/data/output/

Run (standard library only):
    python verify_outputs.py "<path to that output folder>"
"""
import csv
import os
import sys
from collections import Counter

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "COS10022_A1_Workflow", "data", "output")
TARGET, PRED = "Survived", "Prediction (Survived)"
FEATURES = ["Age", "Gender", "Speed_of_Impact", "Helmet_Used", "Seatbelt_Used"]
problems = 0


def read(name):
    with open(os.path.join(OUT, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check(ok, msg):
    global problems
    print(("  OK    " if ok else "  FAIL  ") + msg)
    problems += 0 if ok else 1


def score(rows, title):
    cm = Counter((r[TARGET], r[PRED]) for r in rows)
    tp, fn = cm[("Yes", "Yes")], cm[("Yes", "No")]
    fp, tn = cm[("No", "Yes")], cm[("No", "No")]
    n = tp + fn + fp + tn
    acc = (tp + tn) / n
    rec = tp / (tp + fn) if tp + fn else 0.0
    prec = tp / (tp + fp) if tp + fp else 0.0
    print(f"\n{title}  (positive class = Yes)")
    print(f"                 pred No  pred Yes")
    print(f"  actual No      {tn:7d}  {fp:8d}")
    print(f"  actual Yes     {fn:7d}  {tp:8d}")
    print(f"  accuracy {acc:.3f}   recall(Yes) {rec:.3f}   precision(Yes) {prec:.3f}"
          f"   always-'No' baseline {(tn + fp) / n:.3f}")
    return acc, (tn, fp, fn, tp)


print(f"Reading {OUT}")

# ---- Task 1
t1 = read("task1_LR_predictions.csv")
check(len(t1) == 180, f"task 1 test set has 180 rows (got {len(t1)})")
acc, cm = score(t1, "Task 1 - Logistic Regression (train2.csv -> test2.txt)")
check(cm == (92, 19, 45, 24), "task 1 matches the independent Python check (IRLS = unpenalised LR: "
                              "92/19/45/24, accuracy 0.644)")

# ---- Task 2 data preparation
train, test = read("task2_train_700.csv"), read("task2_test_500.csv")
print()
check(len(train) == 700, f"training set has 700 rows (got {len(train)})")
check(Counter(r[TARGET] for r in train) == Counter({"Yes": 350, "No": 350}),
      f"training set is 350 Yes + 350 No (got {dict(Counter(r[TARGET] for r in train))})")
check(len(test) == 500, f"test set has 500 rows (got {len(test)})")
check(Counter(r[TARGET] for r in test) == Counter({"Yes": 28, "No": 472}),
      f"test set is 28 Yes + 472 No (got {dict(Counter(r[TARGET] for r in test))})")
check(set(train[0]) == set(FEATURES + [TARGET]), f"no extra columns such as a file path (got {list(train[0])})")
first = [r[TARGET] for r in train[:50]]
check(0 < first.count("Yes") < 50, "training set is shuffled (first 50 rows contain both classes)")

key = lambda r: tuple(r[c] for c in FEATURES + [TARGET])
train_keys = set(map(key, train))
leak = sum(key(r) in train_keys for r in test)
print(f"\n  Leakage: {leak} of 500 test rows ({leak / 5:.0f}%) are identical to a training row, because the four "
      f"CSVs hold the same 600 records twice.")

# ---- Task 2 models
results = {}
for tag, title in (("LR", "Logistic Regression"), ("NB", "Naive Bayes"), ("RF", "Random Forest")):
    rows = read(f"task2_{tag}_predictions.csv")
    check(len(rows) == 500, f"{tag} predictions cover the 500-row test set")
    results[tag], _ = score(rows, f"Task 2 - {title}")
    seen = [r for r in rows if key(r) in train_keys]
    unseen = [r for r in rows if key(r) not in train_keys]
    a_seen = sum(r[TARGET] == r[PRED] for r in seen) / max(len(seen), 1)
    a_unseen = sum(r[TARGET] == r[PRED] for r in unseen) / max(len(unseen), 1)
    print(f"  accuracy on rows also in training: {a_seen:.3f}   on genuinely unseen rows: {a_unseen:.3f}")

print("\nReference KNIME run (seed 2026): LR 0.706, NB 0.674, RF 0.752. A different seed or settings"
      " will give somewhat different values.")
print(f"\nRESULT: {'PASS' if problems == 0 else f'{problems} problem(s) - see FAIL lines'}")
sys.exit(1 if problems else 0)
