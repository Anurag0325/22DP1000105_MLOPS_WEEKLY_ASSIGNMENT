from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow

EXPERIMENT_NAME = "iris-mlsecops-poisoning"


def main():
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        raise SystemExit(f"Experiment '{EXPERIMENT_NAME}' not found.")

    runs = client.search_runs(experiment_ids=[experiment.experiment_id])
    rows = []
    for r in runs:
        p, m = r.data.params, r.data.metrics
        rows.append({
            "poison_level": int(p.get("poison_level", -1)),
            "accuracy": m.get("accuracy"),
            "precision": m.get("precision"),
            "recall": m.get("recall"),
            "f1_score": m.get("f1_score"),
        })
    rows.sort(key=lambda x: x["poison_level"])

    print(f"{'poison %':>9} | {'accuracy':>8} | {'precision':>9} | {'recall':>8} | {'f1':>8}")
    for row in rows:
        print(f"{row['poison_level']:>8}% | {row['accuracy']:.4f}  | {row['precision']:.4f}   | "
              f"{row['recall']:.4f}  | {row['f1_score']:.4f}")

    Path("data").mkdir(exist_ok=True)
    with open("data/comparison_table.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["poison_level", "accuracy", "precision", "recall", "f1_score"])
        writer.writeheader()
        writer.writerows(rows)

    levels = [r["poison_level"] for r in rows]
    fig, ax = plt.subplots(figsize=(7, 5))
    for metric in ("accuracy", "precision", "recall", "f1_score"):
        ax.plot(levels, [r[metric] for r in rows], marker="o", label=metric)
    ax.set_xlabel("Poison level (%)")
    ax.set_ylabel("Score")
    ax.set_title("Model performance vs. data poisoning level")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.savefig("data/degradation_plot.png", dpi=150, bbox_inches="tight")
    print("Saved data/comparison_table.csv and data/degradation_plot.png")


if __name__ == "__main__":
    main()
