# 04 — Zero-shot Bilingual App Reviews Mining with Large Language Models

> **2023** · [PDF](https://arxiv.org/pdf/2311.03058)
> **One line:** Do exactly what Sift does — LLM classifies + clusters reviews,
> zero-shot, across languages — and, crucially, **measures cluster quality with
> NMI**, a number Sift currently doesn't have.

> **Depth of this note:** abstract + skim (PDF extraction was partial). Numbers
> below are from the abstract; verify against the paper before quoting.

---

## The problem it solves

Prior review mining needed labeled training data and mostly handled one language.
This shows an LLM can classify and cluster reviews **zero-shot** (no training) and
**bilingually**, which matches real app stores (Sift scrapes 5 languages).

## How it works

- **Classify** each review into categories with a zero-shot LLM prompt.
- **Cluster** reviews by semantic similarity (LLM/embedding based) — like Sift's
  embedding merge, but they *evaluate* the clustering.
- **Evaluate clustering with NMI** (Normalized Mutual Information): compares
  discovered clusters to gold topic labels, independent of cluster count. This is
  the metric Sift is missing.

## Results (from abstract — verify)

- Classification **F1 ≈ 0.85**.
- Clustering **NMI > 0.6** on bilingual reviews.
- Beats traditional topic models on multilingual data; no training phase.
- Noted risks: cost, prompt sensitivity, category **hallucination** on ambiguous
  reviews, worse on low-resource languages.

## Why suggested for Sift

This is the closest paper to **what Sift already is** — so it's our benchmark and
our measuring stick:

- **Validates the architecture.** LLM-classify-then-cluster is a published,
  working approach. We're not off in the weeds.
- **Gives us a clustering metric.** Right now Sift's embedding merge (>0.75) and
  LLM collapse have **no quality number** — we can't tell if a change made
  clustering better or worse. Adopt **NMI** against a small gold set (we can
  build one from the LLM-judge high-agreement rows — a NOTES research direction).
- **Names our risk.** "Category hallucination on ambiguous reviews" is exactly
  the Funnel-1 seed-anchoring / mislabel worry from our earlier discussion.
- **Bilingual** = our multi-language scrape; confirms the LLM handles it without
  per-language pipelines.

## What to steal

- [ ] **NMI** as Sift's clustering-quality metric. Build a small gold-labeled set
      → score every clustering change against it.
- [ ] Their **zero-shot prompt structure** — compare to our seed-anchored prompt
      ([`agent.py:35`](../../pulse_engine/analysis/agent.py#L35)); zero-shot may
      reduce the seed bias we flagged.
- [ ] Track **hallucination rate** on ambiguous reviews as an eval dimension.

## Read this if…

You're measuring whether Sift's clustering is any good, redesigning the
extraction prompt, or defending the LLM approach vs classic topic models.

## Open questions

- Exact prompts + which LLM (the summary said Claude; confirm in paper).
- How they built the gold set for NMI — we need the same for our eval.
