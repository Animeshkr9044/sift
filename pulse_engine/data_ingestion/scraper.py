# pulse_engine/data_ingestion/scraper.py

import concurrent.futures
from datetime import datetime
from google_play_scraper import Sort, reviews
from tqdm import tqdm

LANGUAGES = ['en', 'hi', 'mr', 'bn', 'te']  # English, Hindi, Marathi, Bengali, Telugu

def _fetch_reviews_task(app_id, start_date, score, lang):
    """Fetches reviews for a specific star rating and language."""
    collected_reviews = []
    continuation_token = None
    while True:
        try:
            result, token = reviews(
                app_id,
                lang=lang,
                country='in',
                sort=Sort.NEWEST,
                count=200,
                filter_score_with=score,
                continuation_token=continuation_token
            )
            if not result or not token:
                break
            
            collected_reviews.extend(result)
            continuation_token = token

            last_review_date = result[-1]['at'].date()
            if last_review_date < start_date.date():
                break
        except Exception:
            break
    return collected_reviews

def scrape_reviews(app_id, start_date, end_date):
    """Scrapes reviews in parallel for a given app ID within a specific date range."""
    print(f"Starting highly parallel fetch for {app_id} reviews from {start_date.date()} to {end_date.date()}...")
    
    all_reviews = []
    tasks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        for score in range(1, 6):
            for lang in LANGUAGES:
                tasks.append(executor.submit(_fetch_reviews_task, app_id, start_date, score, lang))
        
        # Use tqdm to show progress for the fetching tasks
        for future in tqdm(concurrent.futures.as_completed(tasks), total=len(tasks), desc=f"Scraping {app_id}"):
            try:
                data = future.result()
                all_reviews.extend(data)
            except Exception as exc:
                print(f'A scraping task generated an exception: {exc}')

    # Filter reviews to be within the date range and remove duplicates
    unique_reviews = {r['reviewId']: r for r in all_reviews if start_date.date() <= r['at'].date() <= end_date.date()}.values()
    
    print(f"\nAll fetching complete. Found {len(unique_reviews)} unique reviews within the specified date range.")
    return list(unique_reviews)
