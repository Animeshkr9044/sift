# 02 — MERIT: Emerging App Issue Identification via Online Joint Sentiment-Topic Tracing

> Cuiyun Gao, Jichuan Zeng, Zhiyuan Wen, David Lo, Xin Xia, Irwin King, Michael R. Lyu ·
> **IEEE TSE 2020** · [PDF](https://arxiv.org/pdf/2008.09976) · code: github.com/armor-ai/MERIT
> **One line:** IDEA, but fixes three of its weaknesses — models word-*pairs*
> (biterms) for short text, folds in **sentiment** so only *negative* topics get
> flagged, and labels topics with word embeddings.

---

## The problem it solves

Same authors as IDEA, addressing IDEA's own stated limits:

1. **Short reviews break LDA.** Avg review ≈ 71 chars. LDA assumes each *word*
   has one topic and needs long docs — it produces incoherent topics on short
   text (top words like "also", "there be", "great app" — noise).
2. **No sentiment.** IDEA flags *any* emerging topic, including surges of
   **praise**. Emerging *issues* are negative. Praise spikes → false positives.
3. **Weak topic labels.** IDEA's labels rely only on topic-distribution
   similarity; the meanings drift and can mislabel, causing false issue alerts.

*(All three are also Sift's problems — see NOTES §5.)*

## How it works

Five stages (their Figure 3). The engine is **AOBST → AOBST-online**:

**Biterm instead of single word.** A *biterm* is an unordered word-pair
co-occurring in a short context. "video can not play" → biterms
`(video,can) (video,not) (video,play) (can,not) (can,play) (not,play)`. Modeling
pairs beats LDA on short text because it learns co-occurrence directly instead of
per-word topic assignment. (This is BTM, adapted.)

**Joint sentiment-topic (BST).** Each biterm is assigned both a **topic** `z`
*and* a **sentiment** `s ∈ {neg, neu, pos}`. Sentiment prior seeded from opinion
lexicons (Hu & Liu, 2006 words + 4783 neg) plus 500 app-specific words they hand-
labeled (κ=0.79 agreement) → 7215 polarity words. Output is a 3-D matrix
Φ ∈ ℝ^{3×K×V} (sentiment × topic × word).

```
P(biterm b=(wi,wj)) = Σ_{s,z} θ_s · φ_{wi|s,z} · φ_{wj|s,z}
```

**Online adaptive tracing (AOBST).** Like IDEA's AOLDA — blend the last `ω`
versions' sentiment-topic distributions to form the current prior:

```
βᵗ_{s,z} = Σ (i=1..ω) η^{t,i}_{s,z} · φ^{t-i}_{s,z}     (η = softmax similarity weights)
```

**Emerging = anomaly, but negative-only.** Compute JS divergence of each
**negative** topic vs previous versions; flag with the same outlier rule:

```
( {D_JS}ᵗ_z − mean(D_JS) ) / σ  >  δ ,   δ = 1.25    (top 10%, negative topics only)
```

**Topic labeling (NTL).** Combines topic-distribution similarity **and** word-
embedding similarity (attention-based match), scored to be representative of the
target topic yet discriminative from others. Fixes IDEA's mislabeling.

## Results

- **Same 6-app dataset** as IDEA (164k reviews, 89 versions). Ground truth =
  changelogs.
- Metrics: `Precision_E`, `Recall_L`, `F_hybrid` (identical to IDEA).
- **Beats IDEA by 22.3% and OLDA by 37.8% on F_hybrid.** Absolute avg
  (sentence-level): P 81.4% / R 81.2% / F 80.9%.
- Ablation confirms all three additions help independently:
  - **BTM (biterm)**: +8.8% / +16.9% F_hybrid (phrase / sentence).
  - **Sentiment**: +5.8% / +19.4%; boosts recall a lot (+9.6% / +13.4% avg).
  - **Embedding labels (NTL)**: +7.3% / +5.9%.
- Runs in acceptable time despite more complexity.
- **Sentence** labels beat **phrase** labels consistently (more context).

**Where it fails (their §6.2):** issues mentioned in only 3-4 reviews slip
through — topic models need volume. And some negative topics recur every version
(e.g. "screen", "battery") without being *new*, slightly hurting precision.

## Why suggested for Sift

MERIT is **almost exactly Sift's roadmap**, pre-validated:

- **Sentiment weighting** (NOTES §6 roadmap): MERIT proves *why* it matters —
  flagging only negative topics is what stops praise surges being called issues.
  Sift's "Feedback" bucket currently mixes praise + complaints; MERIT's fix is to
  separate by sentiment *before* ranking. We even already store the star `score`
  — cheaper sentiment signal than their lexicon model.
- **Biterm / short-text**: validates the worry that our topics on short reviews
  are noisy. If we stay LLM-based we sidestep LDA's short-text problem entirely
  (the LLM reads the whole review) — so we may get MERIT's *benefit* without its
  machinery. Worth noting in design.
- **Sentence-level labels beat phrase-level**: directly informs how we label
  topics for the drilldown feature — prefer a representative *sentence* over a
  keyword.
- **Negative-only anomaly**: combine with IDEA's threshold → our severity score
  = volume × **negativity** × velocity. MERIT is the "negativity" leg.

## What to steal

- [ ] **Flag only negative topics** as emerging. Reuse star `score` for polarity
      (free; we already store it) instead of their lexicon model.
- [ ] **Sentence labels** over phrase labels for topic display / drilldown.
- [ ] The **negative-topic JS-divergence + 1.25σ** rule as the emerging test.
- [ ] Their **failure mode note** → set a min-support floor (skip topics with
      <5 reviews) so we don't over-alert on noise; log what we drop (NOTES rule).

## Read this if…

You're adding sentiment weighting, deciding how to label topics, or refining the
emerging-issue detector past the IDEA baseline. Read **after** IDEA (01).

## Open questions

- Star rating vs text sentiment: is the 1-5 star good enough as polarity, or do
  we need per-topic sentiment (a 4-star review can still complain about *one*
  thing)? MERIT does per-topic; stars are per-review.
- Do we need biterms at all if the LLM already reads full reviews? Likely no —
  but we lose the *quantitative topic distribution* biterms give. Decide.
- Recurring-but-not-new negatives ("delivery" every week) will trip us too. Need
  the baseline-relative rule from IDEA, not absolute negativity.
