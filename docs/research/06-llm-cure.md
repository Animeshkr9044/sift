# 06 — LLM-Cure: LLM-based Competitor User Review Analysis for Feature Enhancement

> **2024** · [PDF](https://arxiv.org/pdf/2409.15724)
> **One line:** Use an LLM to mine *competitor* app reviews, find features users
> praise in rivals that yours lacks, and suggest enhancements.

> **Depth of this note:** abstract only. Read full paper before building.

---

## The problem it solves

Analyzing only *your* reviews tells you what's broken. It doesn't tell you what
competitors do better. LLM-Cure adds the competitive axis: mine rivals' reviews
to surface features/strengths users love elsewhere, mapped to gaps in your app.

## How it works (from abstract)

- Collect reviews for your app **and** competitors.
- LLM extracts features + the sentiment/praise attached.
- Compare across apps → highlight where a competitor is loved and you're not →
  suggested enhancement.

## Why suggested for Sift

Directly the **multi-app comparison feature** — and Sift is already positioned
for it: we scrape **Swiggy, Zomato, Blinkit, Zepto** into one DB. We have the
data; this paper is the method.

- Normalizes the comparison around **features/themes**, not raw counts — so
  "Zomato users praise live tracking, Swiggy users complain about it" becomes a
  concrete gap.
- Turns Sift from single-app diagnostics into **competitive intelligence** — a
  much stronger product story for the same scraped data.

## What to steal

- [ ] A **cross-app theme table**: same themes, per-app sentiment, normalized per
      1k reviews (kills the size bias between apps).
- [ ] **Praise mining** on competitors (not just complaints) → feature-gap list.
- [ ] Reuse the existing multi-app DB — no new scraping needed.

## Read this if…

You're building Swiggy-vs-Zomato-vs-Blinkit comparison, or pitching Sift as
competitive intelligence rather than just bug triage.

## Open questions

- Fair normalization across apps of very different review volumes.
- Aligning themes across apps so "delivery" means the same thing in each.
