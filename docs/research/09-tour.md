# 09 — TOUR: Dynamic Topic and Sentiment Analysis of User Reviews for Assisting App Release

> Gao et al. · **WWW 2021 Companion** · [PDF](https://arxiv.org/pdf/2103.15774) ·
> [ACM](https://dl.acm.org/doi/fullHtml/10.1145/3442442.3458612)
> **One line:** A packaged, customizable **tool** that runs online topic modeling
> + lightweight sentiment across versions, highlights emerging issues, and
> prioritizes reviews — basically IDEA/MERIT productized.

> **Depth of this note:** abstract + tool description. Read full for the sentiment
> strategy details.

---

## The problem it solves

The IDEA/MERIT line produced strong methods but not a usable tool. TOUR packages
them: pick a version, get a per-topic "glimpse" (phrase + sentence level),
emerging topics highlighted, important reviews surfaced — for developers to act.

## How it works (from abstract)

- **Online topic modeling** across versions (the IDEA/AOLDA lineage).
- **Lightweight sentiment** via **customizable opinion words** instead of a heavy
  external sentiment model — cheap, tunable per domain.
- **Prioritizes** important reviews for developer examination.
- Outputs a per-version, per-topic view with emerging issues flagged, at both
  **phrase and sentence** granularity.

## Why suggested for Sift

TOUR is the **product blueprint** for what Sift is trying to become, and its
sentiment choice is a cheap win:

- **Customizable opinion words** for sentiment = a lightweight alternative to a
  full sentiment model. For Sift, our star `score` is even cheaper — but a small
  editable domain opinion-word list (e.g. "late", "refund", "charged twice" =
  strong negative) could sharpen per-topic negativity without an LLM call.
- **Phrase + sentence dual labeling** confirms MERIT's finding — show both a short
  label and a representative sentence in the dashboard.
- It's the **UX reference**: version picker → topic glimpse → emerging
  highlighted → drill to reviews. Good template for the auto-updating dashboard.

## What to steal

- [ ] **Customizable opinion-word list** for cheap, tunable sentiment — editable
      by the user, no model call.
- [ ] **Dual phrase+sentence** display per topic in reports/dashboard.
- [ ] TOUR's **UI flow** (version → glimpse → emerging → reviews) as the dashboard
      interaction model.

## Read this if…

You're designing the dashboard UX or want a lightweight sentiment approach that
doesn't cost an LLM call per review. It's the "how do I ship this as a tool" note.

## Open questions

- Their exact opinion-word sentiment scoring — abstract-level here.
- Whether star rating alone beats a curated opinion-word list for our domain.
