# PulseGen: App Review Analysis Engine

PulseGen is a powerful, modular pipeline designed to scrape, store, and analyze Google Play Store reviews. It uses AI to perform topic modeling and trend analysis, generating insightful reports in JSON, CSV, and PDF formats.

## Project Structure

- **`pulse_engine/`**: The core Python package containing all the logic.
  - `analysis/`: AI agent and text preprocessing.
  - `data_ingestion/`: Live data scraper and database loader.
  - `database/`: Master database management.
  - `reporting/`: Report generation (JSON, CSV, PDF).
- **`data/`**: Stores the master SQLite database (`master_reviews.db`).
- **`output/`**: Contains all generated analysis reports, organized by app.
- **`app.py`**: The main entry point to run the entire pipeline.
- **`config.py`**: Main configuration file for defining apps to analyze and other settings.
- **`.env`**: Stores your secret API keys (e.g., OpenAI).
- **`requirements.txt`**: Lists all the Python dependencies.

## Setup and Usage

### 1. Environment Setup

It is highly recommended to use a Python virtual environment.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 2. Configure API Key

The project uses the OpenAI API for analysis. You need to provide your API key.

1.  Create a file named `.env` in the root of the project.
2.  Add your OpenAI API key to the `.env` file like this:

    ```
    OPENAI_API_KEY="your-secret-api-key-here"
    ```

### 3. Running the Analysis

By default, PulseGen analyzes reviews from the last 30 days. You can also provide a custom date range.

#### A) Analyze All Apps in `config.py`

You can define a list of apps to analyze in the `config.py` file.

```python
# config.py
APPS_TO_ANALYZE = [
    {
        "app_name": "Zomato",
        "app_id": "com.application.zomato",
        "output_dir": "output/zomato_report"
    },
    # Add more apps here
]
```

*   **To analyze the last 30 days (default):**

    ```bash
    python app.py
    ```

*   **To analyze a custom date range:**

    ```bash
    python app.py --start-date "2025-07-01" --end-date "2025-07-31"
    ```

#### B) Analyze a Single App via URL

You can also analyze any app directly by providing its Google Play Store URL.

*   **To analyze the last 30 days (default):**

    ```bash
    python app.py --url "https://play.google.com/store/apps/details?id=com.application.zomato" --app_name "Zomato"
    ```

*   **To analyze a custom date range:**

    ```bash
    python app.py --url "https://play.google.com/store/apps/details?id=com.application.zomato" --app_name "Zomato" --start-date "2025-07-01" --end-date "2025-07-31"
    ```

This will scrape and analyze the reviews, storing the results in a new directory inside `output/`.
