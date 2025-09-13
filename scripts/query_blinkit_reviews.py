import sqlite3

DB_FILE = 'data/blinkit_reviews.db'
TABLE_NAME = 'blinkit_reviews'

def get_monthly_review_counts():
    """Queries the database to get a month-wise count of reviews for Blinkit."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = f"""
    SELECT strftime('%Y-%m', at) as month, COUNT(reviewId) as review_count
    FROM {TABLE_NAME}
    GROUP BY month
    ORDER BY month;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()

    print("Blinkit: Month-wise Review Counts:")
    print("-----------------------------------")
    print("Month      | Review Count")
    print("-----------------------------------")
    for row in results:
        print(f"{row[0]:<10} | {row[1]}")

if __name__ == '__main__':
    get_monthly_review_counts()
