# PulseGen — App Review Analysis Engine

PulseGen is a modular CLI pipeline that scrapes Google Play Store reviews, stores
them in a local database, and uses an LLM plus sentence embeddings to surface the
main topics and complaint trends over time. It generates daily trend reports in
JSON, CSV, and PDF.

> Built as a demo/portfolio project. Reviews are public Google Play data; be
> mindful of Google's terms and of user privacy when scraping and sharing data.

**Video demo:** https://drive.google.com/drive/folders/1Is8L_8c_qsMUjla-s-7EPMj5X7uQcoiP?usp=sharing

---

## How it works

```
Google Play  ──►  scraper  ──►  SQLite (master_reviews.db)  ──►  loader
                                                                    │
                                                                    ▼
   reports (JSON/CSV/PDF)  ◄──  generator  ◄──  AI agent (topic analysis)
```

1. **Scrape** — `data_ingestion/scraper.py` fetches reviews in parallel across
   5 star ratings and 5 languages (en, hi, mr, bn, te), de-duplicated and filtered
   to the requested date range.
2. **Store** — `database/db_manager.py` writes to a local SQLite database
   (`apps` + `reviews` tables), inserting only new reviews.
3. **Load & sample** — `data_ingestion/loader.py` preprocesses text (lowercase,
   strip emojis), drops very short reviews, and samples up to 200 reviews per day.
4. **Analyze** — `analysis/agent.py` uses `gpt-4o-mini` to extract a topic per
   review, then consolidates near-duplicate topics with `all-MiniLM-L6-v2`
   embeddings + cosine similarity, and finally groups them into high-level
   categories with a second LLM pass. Days are processed in parallel.
5. **Report** — `reporting/generator.py` builds a topic × date trend table and
   writes JSON, CSV, and a landscape PDF into `output/`.

## Project structure

```
pulse_engine/            Core package
  data_ingestion/        Scraper + DB loader/sampler
  database/              SQLite schema & inserts
  analysis/              LLM agent + text preprocessing
  reporting/             JSON / CSV / PDF report generation
app.py                   CLI entry point (full pipeline)
config.py                Apps to analyze + DB path; loads OPENAI_API_KEY
data/                    Local SQLite DB + scraped JSON (git-ignored)
output/                  Generated reports (sample PDFs are committed as demos)
scripts/                 Standalone dev/helper scripts (superseded by pulse_engine)
tests/                   Ad-hoc API test scripts
```

## Setup

Requires Python 3.9+ and an OpenAI API key.

```bash
# 1. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure secrets
cp .env.example .env
# then edit .env and set OPENAI_API_KEY
```

`config.py` reads keys from `.env` via `python-dotenv`. Never commit `.env`.

## Usage

By default PulseGen analyzes the last 30 days. Reports land in `output/`.

**Analyze all apps defined in `config.py`:**

```bash
python app.py
```

**Analyze a single app by Play Store URL:**

```bash
python app.py \
  --url "https://play.google.com/store/apps/details?id=com.application.zomato" \
  --app_name "Zomato"
```

**Custom date range** (works with either mode):

```bash
python app.py --start-date "2025-07-01" --end-date "2025-07-31"
```

### CLI options

| Flag | Description |
|------|-------------|
| `--url` | Play Store URL to analyze a single app |
| `--app_name` | Display name when using `--url` |
| `--start-date` | Start date `YYYY-MM-DD` (default: 30 days ago) |
| `--end-date` | End date `YYYY-MM-DD` (default: today) |

### Configuring apps

Edit `APPS_TO_ANALYZE` in `config.py`:

```python
APPS_TO_ANALYZE = [
    {
        "app_name": "Zomato",
        "app_id": "com.application.zomato",
        "output_dir": "output/zomato_report",
    },
    # add more apps here
]
```

## Output

Each run produces, per app / date range:

- `trend_report_<range>.json` — topic trends + top-topic summary
- `topic_review_details_<range>.csv` — every review mapped to its topic
- `trend_report_<range>.pdf` — landscape trend table

Sample PDFs are committed in `output/` as examples.

## Tech stack

OpenAI (`gpt-4o-mini`) · `sentence-transformers` (MiniLM) · scikit-learn ·
pandas · `google-play-scraper` · SQLite · `fpdf2`

## License

[MIT](LICENSE)
