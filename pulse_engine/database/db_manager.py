# pulse_engine/database/db_manager.py

import sqlite3
import os

def initialize_master_database(db_path):
    """Initializes the master database with the required schema if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create 'apps' table to store app metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT UNIQUE NOT NULL,
            app_name TEXT NOT NULL
        )
    ''')

    # Create 'reviews' table with a foreign key to the 'apps' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            reviewId TEXT PRIMARY KEY,
            app_id_fk INTEGER,
            userName TEXT,
            userImage TEXT,
            content TEXT,
            score INTEGER,
            thumbsUpCount INTEGER,
            reviewCreatedVersion TEXT,
            at DATETIME,
            replyContent TEXT,
            repliedAt DATETIME,
            FOREIGN KEY (app_id_fk) REFERENCES apps (id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Master database initialized at {db_path}")

def add_app(db_path, app_id, app_name):
    """Adds a new app to the 'apps' table if it doesn't already exist and returns its database ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO apps (app_id, app_name) VALUES (?, ?)", (app_id, app_name))
    conn.commit()
    app_db_id = cursor.execute("SELECT id FROM apps WHERE app_id = ?", (app_id,)).fetchone()[0]
    conn.close()
    return app_db_id

def bulk_insert_reviews(db_path, reviews_data, app_db_id):
    """Bulk inserts review data into the 'reviews' table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    reviews_to_insert = []
    for review in reviews_data:
        reviews_to_insert.append((
            review.get('reviewId'),
            app_db_id,
            review.get('userName'),
            review.get('userImage'),
            review.get('content'),
            review.get('score'),
            review.get('thumbsUpCount'),
            review.get('reviewCreatedVersion'),
            review.get('at'),
            review.get('replyContent'),
            review.get('repliedAt')
        ))
    
    cursor.executemany('''
        INSERT OR IGNORE INTO reviews (reviewId, app_id_fk, userName, userImage, content, score, thumbsUpCount, reviewCreatedVersion, at, replyContent, repliedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', reviews_to_insert)
    
    conn.commit()
    conn.close()
    print(f"Inserted or ignored {cursor.rowcount} reviews into the master database.")
