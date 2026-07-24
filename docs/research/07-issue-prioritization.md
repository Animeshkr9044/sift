# 07 — MApp-IDEA: Issue Detection and Prioritization Based on Mobile App Reviews

> de Lima et al. · **Software Quality Journal, Dec 2024** ·
> [Springer](https://link.springer.com/article/10.1007/s11219-024-09703-2) ·
> [PDF (RG)](https://www.researchgate.net/publication/370243464_Issue_detection_and_prioritization_based_on_app_reviews)
> **One line:** Detect issues, drop each into a **risk matrix** (severity ×
> likelihood) for priority levels, then track issue risk over time as a time
> series to **trigger alerts**.

> **Depth of this note:** abstract + method summary. Read full for the risk-
> matrix formula.

---

## The problem it solves

Detecting issues isn't enough — teams need to know **which to fix first**. This
adds an explicit prioritization layer (a risk matrix) and an alerting layer on
top of issue detection, at large scale.

## How it works (from abstract)

1. Auto-collect reviews.
2. Detect issues, classify reviews.
3. Place each issue in a **risk matrix** → priority level (like classic
   risk = severity × likelihood).
4. Model each issue's risk as a **time series** → trigger **alerts** when risk
   climbs.

Validated: **50 apps, ~5M reviews, 230k issues** classified into priority
levels. Issues flagged early correlated with **later fix releases** by devs
(evidence the priorities are real).

## Why suggested for Sift

Two Sift features at once — **severity score** and **alerting**:

- Sift ranks by raw count. This gives the **prioritization framework**: a risk
  matrix combining how bad (severity/negativity) × how common/likely. That's the
  structure for our `severity = volume × negativity × velocity` score.
- The **time-series-triggers-alert** loop is exactly the "cron + Slack when a
  theme spikes" item in NOTES §6. This paper shows it works at scale and that the
  alerts precede real fixes.
- Scale proof (5M reviews) — the approach isn't a toy.

## What to steal

- [ ] **Risk-matrix** framing for the severity score (severity × likelihood
      quadrants → P0/P1/P2), instead of a flat ranked list.
- [ ] **Time-series-per-issue → threshold → alert** as the alerting design.
- [ ] Their validation idea: check whether Sift's high-priority flags **precede**
      the dev's changelog fix — a real accuracy signal (same trick as IDEA).

## Read this if…

You're building the severity/priority score or the alerting cron. This is the
"prioritize + alert" paper; pair with IDEA/MERIT for the "detect" half.

## Open questions

- Exact axes of their risk matrix and how severity is scored — need the full PDF.
- How to estimate "likelihood" for us — trend slope? recurrence? volume growth?
