# scripts/evaluate_labels.py
"""
Run the LLM-as-judge over a topic-detail CSV and produce an evaluation dataset.

Usage:
    python scripts/evaluate_labels.py output/swiggy_report/topic_review_details_2025-07-16_to_2025-07-23.csv
    python scripts/evaluate_labels.py <csv> --judge-model gpt-4o --limit 300
"""

import argparse
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from pulse_engine.evaluation.judge import LabelJudge


def main():
    parser = argparse.ArgumentParser(description="LLM-as-judge evaluation of topic labels.")
    parser.add_argument("csv", help="Path to a topic_review_details_*.csv file.")
    parser.add_argument("--judge-model", default="gpt-4o-mini", help="OpenAI model to use as judge.")
    parser.add_argument("--limit", type=int, help="Only judge the first N rows (cost control).")
    args = parser.parse_args()

    if not config.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not found. Create a .env file with your key.")
        return

    df = pd.read_csv(args.csv)
    if "review" not in df.columns or "topic" not in df.columns:
        print(f"ERROR: {args.csv} must have 'review' and 'topic' columns.")
        return
    df = df.dropna(subset=["review", "topic"])
    if args.limit:
        df = df.head(args.limit)

    print(f"Judging {len(df)} labeled reviews with {args.judge_model}...")
    judge = LabelJudge(config.OPENAI_API_KEY, judge_model=args.judge_model)
    graded = judge.judge_dataframe(df)
    metrics = LabelJudge.metrics(graded)

    # Output next to the source CSV, in an eval/ subdir
    src_dir = os.path.dirname(args.csv)
    base = os.path.splitext(os.path.basename(args.csv))[0].replace("topic_review_details", "label_eval")
    eval_dir = os.path.join(src_dir, "eval")
    os.makedirs(eval_dir, exist_ok=True)

    csv_path = os.path.join(eval_dir, f"{base}.csv")
    jsonl_path = os.path.join(eval_dir, f"{base}.jsonl")
    metrics_path = os.path.join(eval_dir, f"{base}_metrics.json")

    graded.to_csv(csv_path, index=False)
    with open(jsonl_path, "w") as f:
        for _, r in graded.iterrows():
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
    metrics["judge_model"] = args.judge_model
    metrics["self_evaluation"] = args.judge_model == "gpt-4o-mini"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"\nEval dataset:  {csv_path}")
    print(f"               {jsonl_path}")
    print(f"Metrics:       {metrics_path}\n")
    print(f"=== Summary ({metrics['total']} reviews, judge={args.judge_model}) ===")
    print(f"Correct:            {metrics['accuracy_correct']:.1%}")
    print(f"Correct or partial: {metrics['accuracy_correct_or_partial']:.1%}")
    print(f"Mean score:         {metrics['mean_score']}/5")
    print(f"Reassignment rate:  {metrics['reassignment_rate']:.1%}")
    if metrics.get("self_evaluation"):
        print("NOTE: self-evaluation (judge == extractor) — accuracy is optimistically biased.")


if __name__ == "__main__":
    main()
