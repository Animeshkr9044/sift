# 03 — AOBTM: Adaptive Online Biterm Topic Modeling for Version-Sensitive Short Texts

> Hadi, Fard et al. · **ICSME 2020** · [PDF](https://arxiv.org/pdf/2009.09930) ·
> code available (see paper)
> **One line:** The topic-modeling engine under MERIT — biterm topic model made
> *online* and *version-aware*, tuned for short noisy app reviews.

> **Depth of this note:** abstract + method summary (not a full read). Deepen if
> you decide to actually port a topic model rather than stay LLM-based.

---

## The problem it solves

LDA and PLSA choke on short texts — too few word co-occurrences per document to
infer topics reliably (the *sparsity* problem). They also can't track topics
across many consecutive versions. AOBTM fixes both.

## How it works

- **Biterm (BTM)** — model unordered word-*pairs* across the whole short text
  instead of per-word topics. Directly attacks sparsity. (Same biterm idea MERIT
  uses.)
- **Online** — updates incrementally as new reviews arrive; scales with volume.
- **Adaptive** — weights the contribution of previous versions to the current
  version's topics, and **statistically picks the optimal number of previous
  time-slices** to blend (not a fixed window).

## Results

Outperforms prior online topic models on short-text coherence and version-
sensitive topic tracking on mobile-app review datasets. (Numbers: see paper.)

## Why suggested for Sift

Background / dependency reading, not a feature on its own:

- It's the **"how"** behind MERIT's biterm claim. If [MERIT](02-merit.md)
  convinces you biterms matter, this is the implementation.
- Its "**adaptively choose how many past versions to blend**" idea is useful even
  if we stay LLM-based: it answers "how long a baseline window for
  emerging-issue detection?" statistically instead of hard-coding 4 weeks.
- **Decision fork:** Sift is LLM-based, so we may never need AOBTM's machinery —
  the LLM reads whole reviews, sidestepping short-text sparsity. Read this only
  if we benchmark classic topic models vs the LLM (a NOTES research direction).

## What to steal

- [ ] The **"optimal number of previous slices"** idea for choosing the
      baseline window in emerging detection, rather than a magic constant.

## Read this if…

You're benchmarking LDA/BTM against the LLM approach, or tuning the baseline
window length. Otherwise skippable — MERIT (02) covers the intuition.

## Open questions

- Concrete gain of AOBTM over plain BTM on *our* weekly (not per-version)
  cadence — unmeasured.
