# pulse_engine/evaluation/judge.py
"""
LLM-as-judge for the topic labels produced by the analysis agent.

Reads a `topic_review_details_*.csv` (columns: date, topic, review), asks an LLM
to grade whether each assigned topic accurately captures the review, and writes a
labeled evaluation dataset plus summary metrics.

NOTE: when the judge model is the same as the extractor (gpt-4o-mini), this is a
self-evaluation — accuracy is optimistically biased. Use a stronger judge for a
trustworthy benchmark.
"""

import json
import pandas as pd
from collections import Counter, defaultdict
from openai import OpenAI
from tqdm import tqdm

VERDICTS = ("correct", "partial", "incorrect")


class LabelJudge:
    def __init__(self, openai_api_key, judge_model="gpt-4o-mini", batch_size=15):
        self.client = OpenAI(api_key=openai_api_key)
        self.judge_model = judge_model
        self.batch_size = batch_size

    def _judge_batch(self, batch):
        """Grade one batch of (review, assigned_topic) pairs."""
        items = [
            {"id": i, "review": row["review"], "assigned_topic": row["topic"]}
            for i, row in enumerate(batch)
        ]
        prompt = f"""
You are a strict evaluator of an automated review-tagging system for a food-delivery app.
For each item you are given a user review and the topic label a model assigned to it.
Decide how well the assigned topic captures the review's MAIN point.

For each item return:
- "id": the item id
- "verdict": one of "correct" (label is the main point), "partial" (related but not
  the primary point, or too generic/too specific), "incorrect" (wrong or misleading)
- "score": integer 1-5 (5 = perfect label, 1 = wrong)
- "suggested_topic": the topic YOU would assign (repeat the assigned one if it is correct)
- "reason": one short sentence

Items:
{json.dumps(items, ensure_ascii=False, indent=2)}

Return a JSON object: {{"results": [ {{"id":0,"verdict":"...","score":5,"suggested_topic":"...","reason":"..."}}, ... ]}}
"""
        try:
            resp = self.client.chat.completions.create(
                model=self.judge_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            parsed = json.loads(resp.choices[0].message.content)
            results = parsed.get("results", parsed if isinstance(parsed, list) else [])
            out = []
            for r in results:
                idx = r.get("id")
                if idx is None or idx >= len(batch):
                    continue
                verdict = r.get("verdict", "").lower()
                if verdict not in VERDICTS:
                    verdict = "partial"
                out.append({
                    "review": batch[idx]["review"],
                    "assigned_topic": batch[idx]["topic"],
                    "verdict": verdict,
                    "score": int(r.get("score", 3)),
                    "suggested_topic": r.get("suggested_topic", batch[idx]["topic"]),
                    "reason": r.get("reason", ""),
                })
            return out
        except Exception as e:
            print(f"Judge batch failed: {e}")
            return []

    def judge_dataframe(self, df):
        """Judge every row of a details dataframe; returns a graded dataframe."""
        rows = df.to_dict("records")
        graded = []
        for i in tqdm(range(0, len(rows), self.batch_size), desc="Judging labels"):
            graded.extend(self._judge_batch(rows[i:i + self.batch_size]))
        return pd.DataFrame(graded)

    @staticmethod
    def metrics(graded_df):
        """Compute eval metrics from a graded dataframe."""
        n = len(graded_df)
        if n == 0:
            return {"total": 0}
        vc = Counter(graded_df["verdict"])
        per_topic = defaultdict(lambda: {"n": 0, "correct": 0})
        for _, r in graded_df.iterrows():
            t = r["assigned_topic"]
            per_topic[t]["n"] += 1
            if r["verdict"] == "correct":
                per_topic[t]["correct"] += 1
        topic_acc = {
            t: {
                "n": v["n"],
                "accuracy": round(v["correct"] / v["n"], 3),
            }
            for t, v in sorted(per_topic.items(), key=lambda kv: -kv[1]["n"])
        }
        # rows where the judge would reassign
        disagreements = int((graded_df["assigned_topic"] != graded_df["suggested_topic"]).sum())
        return {
            "total": n,
            "verdict_counts": dict(vc),
            "accuracy_correct": round(vc.get("correct", 0) / n, 3),
            "accuracy_correct_or_partial": round((vc.get("correct", 0) + vc.get("partial", 0)) / n, 3),
            "mean_score": round(float(graded_df["score"].mean()), 3),
            "reassignment_rate": round(disagreements / n, 3),
            "per_topic_accuracy": topic_acc,
        }
