import json
import sqlite3

JSON_FILE = 'data/reviews.json'
DB_FILE = 'data/reviews.db'
TABLE_NAME = 'reviews'

def create_database_and_load_data():
    """Reads reviews from a JSON file and loads them into a SQLite database."""
    # Connect to the SQLite database (this will create the file if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the table with a schema that matches the JSON data
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
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        reviews_by_date = json.load(f)

    print(f"Loading reviews from {JSON_FILE} into {DB_FILE}...")
    reviews_to_insert = []
    for daily_reviews in reviews_by_date.values():
        for review in daily_reviews:
            reviews_to_insert.append(tuple(review.get(key) for key in [
                'reviewId', 'userName', 'userImage', 'content', 'score',
                'thumbsUpCount', 'reviewCreatedVersion', 'at', 'replyContent',
                'repliedAt', 'appVersion'
            ]))

    # Use INSERT OR REPLACE to handle duplicates and ensure the latest data is stored
    cursor.executemany(f'''
    INSERT OR REPLACE INTO {TABLE_NAME} (reviewId, userName, userImage, content, score, thumbsUpCount, reviewCreatedVersion, at, replyContent, repliedAt, appVersion)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', reviews_to_insert)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"Successfully loaded {len(reviews_to_insert)} reviews into {DB_FILE}.")

if __name__ == '__main__':
    create_database_and_load_data()
