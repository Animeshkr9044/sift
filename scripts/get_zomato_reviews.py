import json
from collections import defaultdict
from datetime import datetime
from google_play_scraper import Sort, reviews
import concurrent.futures

APP_ID = "com.application.zomato"
START_DATE = datetime(2024, 6, 1).date()
LANGUAGES = ['en', 'hi', 'mr', 'bn', 'te']  # English, Hindi, Marathi, Bengali, Telugu

def fetch_reviews_task(score, lang):
    """Fetches reviews for a specific star rating and language."""
    thread_id = f"score {score}, lang {lang}"
    print(f"[{thread_id}] Starting fetch...")
    collected_reviews = []
    continuation_token = None
    while True:
        try:
            result, token = reviews(
                APP_ID,
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
            print(f"[{thread_id}] Fetched reviews up to {last_review_date.isoformat()}...")

            if last_review_date < START_DATE:
                break
        except Exception as e:
            print(f"[{thread_id}] An error occurred: {e}. Retrying might be needed.")
            break  # Stop this thread on error
    print(f"[{thread_id}] Finished fetching.")
    return collected_reviews

print(f"Starting highly parallel fetch for Zomato reviews from {START_DATE.isoformat()} to today.")

all_reviews = []
with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
    tasks = [executor.submit(fetch_reviews_task, score, lang) for score in range(1, 6) for lang in LANGUAGES]
    for future in concurrent.futures.as_completed(tasks):
        try:
            data = future.result()
            all_reviews.extend(data)
        except Exception as exc:
            print(f'A task generated an exception: {exc}')

print("\nAll fetching complete. Processing and saving reviews...")

reviews_by_date = defaultdict(list)
all_reviews.sort(key=lambda r: r['at'], reverse=True)

for review in all_reviews:
    review_date = review['at'].date()
    if review_date >= START_DATE:
        review_date_str = review_date.isoformat()
        if len(reviews_by_date[review_date_str]) < 200:
            review['at'] = review['at'].isoformat()
            if review.get('repliedAt'):
                review['repliedAt'] = review['repliedAt'].isoformat()
            reviews_by_date[review_date_str].append(review)

output_file = 'data/zomato_reviews.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(reviews_by_date, f, ensure_ascii=False, indent=4)

print(f"\nSuccessfully saved reviews from {START_DATE.isoformat()} to {output_file}")
