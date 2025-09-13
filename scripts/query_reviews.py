import sqlite3

DB_FILE = 'data/reviews.db'
TABLE_NAME = 'reviews'

def get_monthly_review_counts():
    """Queries the database to get a month-wise count of reviews."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # The 'at' column stores dates as ISO 8601 strings (e.g., '2025-09-10T20:40:36').
    # We can use strftime to extract the year and month ('YYYY-MM').
    query = f"""
    SELECT strftime('%Y-%m', at) as month, COUNT(reviewId) as review_count
    FROM {TABLE_NAME}
    GROUP BY month
    ORDER BY month;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()

    print("Month-wise Review Counts:")
    print("-------------------------")
    print("Month      | Review Count")
    print("-------------------------")
    for row in results:
        print(f"{row[0]:<10} | {row[1]}")

if __name__ == '__main__':
    get_monthly_review_counts()
