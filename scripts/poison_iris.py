import argparse
import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_SEED = 42
MASTER_PATH = Path("data/iris_clean_master.csv")
OUT_PATH = Path("data/iris.csv")

FEATURE_COLS = ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"]
LABEL_COL = "target"


def poison(df: pd.DataFrame, pct: float, seed: int = RANDOM_SEED) -> pd.DataFrame:
    if pct <= 0:
        return df.copy()
    rng = np.random.default_rng(seed)
    poisoned = df.copy()
    n_rows = len(df)
    n_poison = int(round(n_rows * pct / 100))
    idx = rng.choice(n_rows, size=n_poison, replace=False)

    ranges = {}
    for col in FEATURE_COLS:
        lo, hi = df[col].min(), df[col].max()
        span = hi - lo
        ranges[col] = (lo - 0.25 * span, hi + 0.25 * span)

    classes = df[LABEL_COL].unique()
    for i in idx:
        for col in FEATURE_COLS:
            lo, hi = ranges[col]
            poisoned.at[i, col] = rng.uniform(lo, hi)
        poisoned.at[i, LABEL_COL] = rng.choice(classes)
    return poisoned


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pct", type=float, required=True)
    args = parser.parse_args()

    base = pd.read_csv(MASTER_PATH)
    result = poison(base, args.pct)
    result.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} at {args.pct}% corruption ({len(result)} rows)")


if __name__ == "__main__":
    main()
