# pulse_engine/data_ingestion/loader.py

import sqlite3
import pandas as pd
from collections import defaultdict
from ..analysis.preprocessor import preprocess_text

def load_and_sample_reviews(db_path, app_id, start_date, end_date):
    """Loads, preprocesses, filters, and samples review data from the master database for a specific app and date range."""
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Loading data for {app_id} from {start_date_str} to {end_date_str} from master database...")
    
    try:
        conn = sqlite3.connect(db_path)
        query = f"""
            SELECT
                SUBSTR(r.at, 1, 10) as date,
                r.content
            FROM reviews r
            JOIN apps a ON r.app_id_fk = a.id
            WHERE a.app_id = ? AND r.at BETWEEN ? AND ?
        """
        df = pd.read_sql_query(query, conn, params=(app_id, start_date_str, end_date_str))
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error while loading reviews: {e}")
        return defaultdict(list)

    if df.empty:
        print("No reviews found for the specified app and date range.")
        return defaultdict(list)

    # Preprocess and filter the data
    df['content'] = df['content'].apply(preprocess_text)
    df = df[df['content'].str.split().str.len() >= 5]

    # Group by date and sample up to 200 reviews
    daily_reviews = defaultdict(list)
    for date, group in df.groupby('date'):
        sample_size = min(len(group), 200)
        daily_reviews[date] = group.sample(n=sample_size, random_state=42)['content'].tolist()
    
    print(f"Loaded and sampled reviews for {len(daily_reviews)} days.")
    return daily_reviews
