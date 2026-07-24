# Research Notes — App-Review Mining

Reading notes on the academic work behind Sift. Each file summarizes one paper
**and** says *why it matters for Sift specifically* — which design decision it
challenges, which feature it unlocks, what to steal.

Read the note first (10 min), then the paper if the note hooks you. Every note
ends with a **"Why suggested for Sift"** block that ties the paper back to our
actual code in [`pulse_engine/`](../../pulse_engine/).

---

## How Sift works today (the baseline these papers critique)

Sift's pipeline: scrape → store → LLM extracts a topic per review →
embedding-merge similar topic *names* (>0.75 cosine) → LLM collapses them into a
few coarse themes → count per day → PDF/CSV. See [NOTES.md](../NOTES.md) §2.

Two known weaknesses these papers speak to directly:

1. **Topics get collapsed, not tracked.** We flatten fine topics into a small
   fixed set every run ([`agent.py:139`](../../pulse_engine/analysis/agent.py#L139)).
   Losing the fine grain is why we can't detect *new* issues or drill down.
2. **Ranking by raw count, not negativity or novelty.** No sentiment weighting,
   no baseline comparison. A theme that's big-but-stable looks the same as one
   spiking this week.

---

## The papers, mapped to Sift decisions

| # | Paper | Year | Answers our question | Unlocks feature |
|---|-------|------|----------------------|-----------------|
| [01](01-idea.md) | **IDEA** — Online App Review Analysis for Identifying Emerging Issues | 2018 | "Is this issue NEW this week?" | Emerging-issue detection |
| [02](02-merit.md) | **MERIT** — Emerging App Issue ID via Joint Sentiment-Topic Tracing | 2020 | "…and is it a *complaint* (not praise)?" | Sentiment-weighted emerging detection |
| [03](03-aobtm.md) | **AOBTM** — Adaptive Online Biterm Topic Modeling | 2020 | "How to model topics in *short* reviews?" | Better topic quality on short text |
| [04](04-zeroshot-llm-mining.md) | **Zero-shot Bilingual App Review Mining with LLMs** | 2023 | "Is our LLM approach any good? How to measure clustering?" | Cluster-quality metric (NMI), multi-language |
| [05](05-llm-human-centric.md) | **Rethinking App Review Mining with LLMs (Human-Centric)** | 2024 | "*Why* are users angry, not just what?" | Sub-reason drilldown |
| [06](06-llm-cure.md) | **LLM-Cure** — Competitor Review Analysis for Feature Enhancement | 2024 | "How do we compare vs competitors?" | Multi-app comparison |
| [07](07-issue-prioritization.md) | **Issue Detection and Prioritization Based on App Reviews** | 2024 | "Which issue do we fix first?" | Severity / priority score |
| [08](08-temporal-dynamics.md) | **Temporal Dynamics of RE from Mobile App Reviews** | 2024 | "Did our fix actually work?" | Before/after diff |
| [09](09-tour.md) | **TOUR** — Dynamic Topic & Sentiment Analysis for App Release | 2021 | "How to run topic+sentiment online, tied to releases?" | Release-tied dashboard |

---

## Reading order

1. **[IDEA](01-idea.md)** — the mental model. Version → topic distribution →
   anomaly = emerging issue. Everything else builds on this.
2. **[MERIT](02-merit.md)** — the upgrade. Same authors, adds biterms +
   sentiment. This paper is basically Sift's roadmap written up by academics.
3. **[Zero-shot LLM Mining](04-zeroshot-llm-mining.md)** — validates our
   LLM-based approach and hands us **NMI** to measure whether our clustering is
   actually good (right now we have no number for that).

Then dip into 05–09 as you build each feature.

---

## The one-line takeaway across all of them

> Classic emerging-issue work (IDEA/MERIT) never collapses topics into a small
> fixed set the way Sift does. It tracks a **topic distribution per version over
> time** and flags **statistical deviation** (anomaly). That's the whole trick to
> detecting *new* issues — and it's exactly the capability our current
> collapse-everything pipeline throws away.

See [`_TEMPLATE.md`](_TEMPLATE.md) for the note format when you add a paper.
