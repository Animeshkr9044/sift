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

PulseGen can be run in two modes:

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

To run the pipeline for all configured apps, execute:

```bash
python app.py
```

#### B) Analyze a Single App via URL

You can also analyze any app directly by providing its Google Play Store URL as a command-line argument.

```bash
python app.py --url "https://play.google.com/store/apps/details?id=com.application.zomato" --app_name "Zomato"
```

This will scrape the reviews for the specified app, store them in the master database, and generate the analysis reports in a new directory inside `output/`.
