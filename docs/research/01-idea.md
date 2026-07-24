# 01 — IDEA: Online App Review Analysis for Identifying Emerging Issues

> Cuiyun Gao, Jichuan Zeng, Michael R. Lyu, Irwin King · **ICSE 2018** ·
> [PDF](https://www.cse.cuhk.edu.hk/lyu/_media/conference/cgao_icse2018_online.pdf) ·
> code: github.com/ReMine-Lab/IDEA
> **One line:** Track each app version's topic distribution, and flag any topic
> that suddenly deviates from previous versions as an *emerging* issue.

---

## The problem it solves

Apps get thousands of reviews/day. Manual reading is impossible. Prior work only
classified reviews into **predefined** categories (privacy, GUI, crash…) — but
new bugs are *not predefined*, they differ per app and per version. So the
question "what broke **this week** that wasn't broken before?" had barely been
studied. IDEA answers exactly that, automatically, online.

**Their definition of an emerging issue** (Def 2.1): an issue that *rarely
appeared in previous time slices* but is now *mentioned by a significant
proportion* of reviews in the current slice. Novelty + volume, together.

## How it works

Four stages (their Figure 4):

**1. Preprocess** — lowercase, lemmatize, replace digits with `<digit>`, fix
repeated/misspelled/non-English words. Then extract **phrases** (2-word) via PMI
(Pointwise Mutual Information) so topic labels are readable, not just single
words. Filter 78 non-informative stop words (`cool`, `asap`, `thank`, `love`…).

**2. Emerging topic detection — AOLDA (the core idea).**
Regular Online LDA models this slice's topics using *only* the last slice. On
short, noisy reviews that's unstable. AOLDA instead builds the current version's
topic prior by **adaptively blending the last `w` versions**, each weighted by
how similar it is:

```
βᵗ_k = Σ (i=1..w)  γ^{t,i}_k · φ^{t-i}_k          (blend prior from w past versions)
γ^{t,i}_k = softmax over similarity of topic k between versions   (adaptive weights)
```

Then **anomaly = emerging**. For each topic, measure how different this
version's word distribution is from previous ones, using **Jensen-Shannon
divergence**:

```
D_JS(P‖Q) = ½ D_KL(P‖M) + ½ D_KL(Q‖M),   M = ½(P+Q)
```

A topic is flagged emerging when its divergence exceeds a threshold set from the
distribution of all divergences (assume Gaussian):

```
δᵗ = μ + 1.25·σ         (1.25 ⇒ top ~10% of topics flagged as anomalies)
```

**3. Topic interpretation** — label each topic with its 3 most representative
**phrases** and **sentences**, ranked by a combined score: semantic relevance to
the topic *minus* similarity to other topics (so labels are discriminative),
plus a sentiment/length term (low-rating + longer reviews score higher).

**4. Visualization — "Issue River"** — a streamgraph; each colored band is a
topic, band width = user concern that version, emerging bands highlighted.

## Results

- **6 apps**, 2 App Store + 4 Google Play, 164k reviews, 89 versions (Aug 2016–Apr 2017).
- Ground truth = official **changelogs** (what devs actually fixed next version).
- Metrics: `Precision_E` (are flagged issues real?), `Recall_L` (do our issues
  cover the changelog?), `F_hybrid` (balance).
- **Beats OLDA baseline by 72.0% on F-score** (avg P 60.4% / R 60.3% / F 58.5%).
- User study at Tencent: **88.9% of engineers/PMs** said the flagged issues help
  real development.

## Why suggested for Sift

This is the paper for our **#1 feature (emerging-issue detection)** and it
directly indicts Sift's current design:

- Sift **collapses** topics into a small fixed set every run
  ([`agent.py:109-146`](../../pulse_engine/analysis/agent.py#L109-L146)). IDEA
  does the opposite — it *keeps* a full topic distribution **per version** and
  compares across versions. You cannot detect "new this week" if you threw away
  the fine topics and have no baseline. This is the core reason Sift can't do
  emerging detection today.
- Sift ranks by **raw mention count**. IDEA ranks by **statistical deviation
  from baseline** (JS divergence vs prior versions). Big-but-stable ≠ emerging.
- We already have the raw material: reviews carry `appVersion` and a timestamp.
  We can slice by version (IDEA's unit) or by week (our unit) — same math.

**The minimum viable steal (no LDA rewrite needed):** keep Sift's per-week topic
counts, compute each topic's share, then flag a topic emerging when this week's
share is `> μ + k·σ` of its own trailing-N-week baseline. That's IDEA's anomaly
rule applied to counts we already produce. Full AOLDA is the "do it properly"
version later.

## What to steal

- [ ] **Anomaly rule** `δ = μ + 1.25σ` over a topic's own history → emerging flag.
- [ ] **JS divergence** as the "how different is this week" measure (robust, symmetric).
- [ ] **Changelog-as-ground-truth** eval — validates flags against what devs fixed.
- [ ] **Issue River** streamgraph for the dashboard — perfect for showing drift.
- [ ] **PMI phrase extraction** for readable topic labels (better than bare words).
- [ ] Keep topics **per time-slice**, stop collapsing them globally.

## Read this if…

You're implementing emerging-issue detection, choosing the anomaly threshold, or
designing the time-series dashboard. Start here before MERIT.

## Open questions

- IDEA slices by **version**; Sift currently slices by **date range**. Version is
  a cleaner signal (ties issue → release) — worth joining `appVersion` in.
- AOLDA is LDA-based; we're LLM-based. Do we port AOLDA, or apply just the
  anomaly rule on LLM topic counts? (Note recommends the latter first.)
- Threshold `1.25σ` = top 10% flagged. Right number for a weekly cadence with
  fewer topics than their setup? Needs tuning.
