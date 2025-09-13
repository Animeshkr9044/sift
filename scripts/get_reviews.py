import json
from collections import defaultdict
from datetime import datetime
from google_play_scraper import Sort, reviews
import concurrent.futures

APP_ID = "in.swiggy.android"
START_DATE = datetime(2024, 6, 1).date()

def fetch_reviews_for_score(score):
    """Fetches all reviews for a specific star rating until the START_DATE is reached."""
    print(f"[Thread for score {score}] Starting fetch...")
    collected_reviews = []
    continuation_token = None
    while True:
        result, token = reviews(
            APP_ID,
            lang='en',
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
        print(f"[Thread for score {score}] Fetched reviews up to {last_review_date.isoformat()}...")

        if last_review_date < START_DATE:
            break
    print(f"[Thread for score {score}] Finished fetching.")
    return collected_reviews

print(f"Starting parallel fetch for reviews from {START_DATE.isoformat()} to today.")

all_reviews = []
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Map each score (1-5) to the fetch function
    future_to_score = {executor.submit(fetch_reviews_for_score, score): score for score in range(1, 6)}
    for future in concurrent.futures.as_completed(future_to_score):
        score = future_to_score[future]
        try:
            data = future.result()
            all_reviews.extend(data)
        except Exception as exc:
            print(f'[Thread for score {score}] generated an exception: {exc}')

print("\nAll fetching complete. Processing and saving reviews...")

# Filter, sort, and group reviews
reviews_by_date = defaultdict(list)
# Sort all reviews by date descending to process newest first
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

# Save the reviews to a JSON file
output_file = 'data/reviews.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(reviews_by_date, f, ensure_ascii=False, indent=4)

print(f"\nSuccessfully saved reviews from {START_DATE.isoformat()} to {output_file}")
