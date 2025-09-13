# App Review Analysis Project

This project contains a suite of tools to download, store, and analyze Google Play Store reviews for various food delivery apps.

## Project Structure

- `data/`: Contains all data files, including the raw JSON reviews and the SQLite databases.
- `scripts/`: Contains all Python scripts for data collection, database loading, and analysis.
- `tests/`: Contains experimental and test scripts.
- `requirements.txt`: Lists all the Python dependencies required for this project.

## Setup and Usage

### 1. Environment Setup

It is recommended to use a Python virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 2. Download Reviews

To download reviews for an app, run the corresponding script from the root directory:

```bash
# Download Swiggy reviews
python scripts/get_reviews.py

# Download Blinkit reviews
python scripts/get_blinkit_reviews.py

# Download Zomato reviews
python scripts/get_zomato_reviews.py
```

### 3. Load Reviews into Database

After downloading the JSON files, load them into their respective SQLite databases:

```bash
python scripts/load_to_db.py
python scripts/load_blinkit_to_db.py
python scripts/load_zomato_to_db.py
```

### 4. Analyze Reviews

To run the topic modeling and trend analysis, you need to configure your OpenAI API key.

1.  Open `scripts/review_analysis.py`.
2.  In the `main()` function, replace `"your-api-key"` with your actual OpenAI key.

Then, run the script:

```bash
python scripts/review_analysis.py
```

This will generate a trend report for the Swiggy reviews and save it in the root directory.
