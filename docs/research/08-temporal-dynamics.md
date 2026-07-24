# 08 — Temporal Dynamics of Requirements Engineering from Mobile App Reviews

> **PeerJ Computer Science 2024** · [PeerJ](https://peerj.com/articles/cs-874/)
> **One line:** Study how review topics/requirements **shift over time** — which
> issues rise, fall, persist — across an app's history.

> **Depth of this note:** abstract only. Read full for the temporal method.

---

## The problem it solves

A single snapshot of review topics is static. Product decisions need the
*trajectory*: is this issue growing or dying? Did it appear after a release? Did
a fix actually reduce complaints? This paper studies those temporal patterns
systematically.

## How it works (from abstract)

Track topic / requirement categories across time windows and characterize their
dynamics — emergence, growth, decline, persistence — over an app's version
history.

## Why suggested for Sift

The paper for the **before/after diff feature** ("did our fix work?"):

- Sift runs are **standalone snapshots** — each report stands alone, no notion of
  trajectory. This frames the temporal comparison we need.
- Directly supports: pick two date ranges (pre-fix, post-fix), show per-theme
  delta %, prove a complaint category dropped after a release.
- Complements IDEA (detects the *spike*) — this frames the *decline* /
  resolution side, which is how you measure ROI of a fix.

## What to steal

- [ ] **Trajectory classification** per theme: emerging / growing / declining /
      persistent — a richer label than a single-run count.
- [ ] **Two-range diff** view (pre vs post) with per-theme delta.
- [ ] Persist run history so trajectories are computable (today each run is
      thrown into `output/` standalone — need a time-linked store).

## Read this if…

You're building before/after comparison or any trend-over-runs view. Pair with
IDEA (spike detection) for the full rise-and-fall picture.

## Open questions

- Their exact temporal model / statistics — abstract-level only here.
- Minimum history length before trajectories are trustworthy.
