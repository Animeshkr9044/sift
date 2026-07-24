# 05 — Rethinking App Review Mining with LLMs: A Human-Centric Perspective

> TUM, Software Engineering & AI · **2024** ·
> [page](https://www.cs.cit.tum.de/en/seai/abschlussarbeiten/rethinking-app-review-mining-with-llms-a-human-centric-perspective/)
> **One line:** Model not just **what** a review says, but **why** it was written
> — the reviewer's expectations, domain knowledge, frustration tolerance, usage
> context.

> **Depth of this note:** abstract only (thesis page). Read the full thesis
> before building on it.

---

## The problem it solves

Classic mining answers *what topic* a review is about. It does not answer *why
this user is upset* — a 1-star "app is trash" from a novice and a detailed
2-star from a power user carry different signal and need different responses.
Topic labels flatten that away.

## How it works (from abstract)

Use LLMs to infer **implicit reviewer traits** alongside the topic:
- **expectations** (what they thought would happen)
- **domain knowledge** (novice vs expert)
- **frustration tolerance**
- **usage context** (when/how they hit the issue)

## Why suggested for Sift

This is the paper for the **"why are they angry" gap** — our sub-reason
drilldown feature, taken one level deeper:

- Sift stops at the topic label ("Delivery Issues"). This says: also extract the
  *cause* and *user context* — turns a bucket into an actionable cause
  ("late because rider couldn't find address", "expert user hit a config edge").
- Pairs naturally with **segmentation** (segment by rating/recency): reviewer
  traits are the segmentation dimension.
- LLM-native — fits Sift's stack; it's a richer extraction prompt, not new infra.

## What to steal

- [ ] Extend the extraction prompt to also return a **root cause** and a
      **user-context** field per review, not just topic + type.
- [ ] Use inferred traits (novice/expert, frustration) as **segment** dimensions
      in reports.

## Read this if…

You're building sub-reason drilldown or user segmentation. It reframes "topic" as
"topic + why + who."

## Open questions

- Reliability of LLM-inferred traits — needs its own eval (easy to hallucinate a
  "usage context" that isn't in the text).
- Cost of a much richer per-review prompt vs Sift's cheap batch-of-20.
