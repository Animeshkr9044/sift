import json
import sqlite3

JSON_FILE = 'data/blinkit_reviews.json'
DB_FILE = 'data/blinkit_reviews.db'
TABLE_NAME = 'blinkit_reviews'

def create_table_and_load_data():
    """Reads Blinkit reviews from a JSON file and loads them into a new table in the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the new table for Blinkit reviews
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        reviewId TEXT PRIMARY KEY,
        userName TEXT,
        userImage TEXT,
        content TEXT,
        score INTEGER,
        thumbsUpCount INTEGER,
        reviewCreatedVersion TEXT,
        at TEXT,
        replyContent TEXT,
        repliedAt TEXT,
        appVersion TEXT
    )
    ''')

    # Load the JSON data
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            reviews_by_date = json.load(f)
    except FileNotFoundError:
        print(f"Error: {JSON_FILE} not found. Please run the script to download the reviews first.")
        return

    print(f"Loading reviews from {JSON_FILE} into table '{TABLE_NAME}' in {DB_FILE}...")
    reviews_to_insert = []
    for daily_reviews in reviews_by_date.values():
        for review in daily_reviews:
            reviews_to_insert.append(tuple(review.get(key) for key in [
                'reviewId', 'userName', 'userImage', 'content', 'score',
                'thumbsUpCount', 'reviewCreatedVersion', 'at', 'replyContent',
                'repliedAt', 'appVersion'
            ]))

    # Use INSERT OR REPLACE to handle duplicates
    cursor.executemany(f'''
    INSERT OR REPLACE INTO {TABLE_NAME} (reviewId, userName, userImage, content, score, thumbsUpCount, reviewCreatedVersion, at, replyContent, repliedAt, appVersion)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', reviews_to_insert)

    conn.commit()
    conn.close()

    print(f"Successfully loaded {len(reviews_to_insert)} reviews into the '{TABLE_NAME}' table.")

if __name__ == '__main__':
    create_table_and_load_data()
