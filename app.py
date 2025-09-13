# app.py

import argparse
import re
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from tqdm import tqdm

import config
from pulse_engine.database import db_manager
from pulse_engine.data_ingestion import scraper, loader
from pulse_engine.analysis.agent import ReviewAnalysisAgent
from pulse_engine.reporting.generator import generate_trend_report, save_reports

def get_app_id_from_url(url):
    """Extracts the app ID from a Google Play Store URL."""
    match = re.search(r'id=([a-zA-Z0-9._]+)', url)
    return match.group(1) if match else None

def process_daily_batch_worker(args):
    """Worker function for parallel processing of daily reviews."""
    date, reviews, openai_api_key = args
    agent = ReviewAnalysisAgent(openai_api_key=openai_api_key)
    extracted_topics = agent.extract_topics_from_reviews(reviews)
    consolidated_topics = agent.consolidate_similar_topics(extracted_topics)
    topic_counts = Counter([t["topic"] for t in consolidated_topics])
    return {
        "date": date,
        "topic_counts": dict(topic_counts),
        "detailed_topics": consolidated_topics
    }

def run_analysis_for_app(app_config, start_date, end_date):
    """Runs the full scrape, store, and analyze pipeline for a single app."""
    app_id = app_config["app_id"]
    app_name = app_config["app_name"]
    output_dir = app_config["output_dir"]

    print(f"\n{'='*20} Starting Pipeline for {app_name} ({app_id}) {'='*20}\n")

    # --- Step 1: Scrape and Store Data ---
    print("--- Step 1: Scraping and Storing Reviews ---")
    reviews_data = scraper.scrape_reviews(app_id, start_date, end_date)
    
    if reviews_data:
        app_db_id = db_manager.add_app(config.MASTER_DB_PATH, app_id, app_name)
        db_manager.bulk_insert_reviews(config.MASTER_DB_PATH, reviews_data, app_db_id)
    else:
        print(f"No new reviews to process for {app_name}. Skipping analysis.")

    # --- Step 2: Load Data and Run Analysis ---
    print("\n--- Step 2: Loading Data and Running Analysis ---")
    daily_reviews = loader.load_and_sample_reviews(
        db_path=config.MASTER_DB_PATH,
        app_id=app_id,
        start_date=start_date,
        end_date=end_date
    )

    if not daily_reviews:
        date_range_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        print(f"No reviews found for {app_name} in the date range {date_range_str} after sampling. Skipping.")
        return

    # --- Step 3: Parallel Analysis ---
    print("\n--- Step 3: Processing Reviews with AI Agent ---")
    agent = ReviewAnalysisAgent(openai_api_key=config.OPENAI_API_KEY)
    process_tasks = [(date, reviews, config.OPENAI_API_KEY) for date, reviews in daily_reviews.items()]
    daily_results = []
    with ProcessPoolExecutor() as executor:
        results_iterator = executor.map(process_daily_batch_worker, process_tasks)
        daily_results = list(tqdm(results_iterator, total=len(process_tasks), desc=f"Analyzing {app_name}"))

    if not daily_results:
        print("Analysis produced no results. Skipping report generation.")
        return

    # --- Step 4: Final Consolidation and Reporting ---
    print("\n--- Step 4: Generating Final Reports ---")
    daily_results.sort(key=lambda x: x['date'])
    consolidated_results = agent.consolidate_topics_with_llm(daily_results)
    
    date_range_str = f"{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}"
    trend_report = generate_trend_report(consolidated_results, end_date.strftime('%Y-%m-%d'), days=len(daily_results))
    save_reports(trend_report, consolidated_results, output_dir, date_range_str)

    print(f"\n{'='*20} Finished Pipeline for {app_name} {'='*20}\n")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Run the PulseGen review analysis pipeline.")
    parser.add_argument("--url", type=str, help="A Google Play Store URL to analyze a single app.")
    parser.add_argument("--app_name", type=str, help="The name of the app if providing a URL.")
    parser.add_argument("--start-date", type=str, help="Start date for analysis (YYYY-MM-DD). Defaults to 30 days ago.")
    parser.add_argument("--end-date", type=str, help="End date for analysis (YYYY-MM-DD). Defaults to today.")
    args = parser.parse_args()

    if not config.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not found. Please create a .env file and add your API key.")
        return

    # Initialize the master database
    db_manager.initialize_master_database(config.MASTER_DB_PATH)
    
    # Set default date range to the last 30 days if not provided
    if args.end_date:
        end_date_obj = datetime.strptime(args.end_date, "%Y-%m-%d")
    else:
        end_date_obj = datetime.now()

    if args.start_date:
        start_date_obj = datetime.strptime(args.start_date, "%Y-%m-%d")
    else:
        start_date_obj = end_date_obj - timedelta(days=30)

    if args.url:
        # Analyze a single app from the URL
        app_id = get_app_id_from_url(args.url)
        if not app_id:
            print(f"ERROR: Could not extract a valid app ID from the URL: {args.url}")
            return
        app_name = args.app_name or app_id
        app_config = {
            "app_name": app_name,
            "app_id": app_id,
            "output_dir": f"output/{app_name.lower().replace(' ', '_')}_report"
        }
        run_analysis_for_app(app_config, start_date_obj, end_date_obj)
    else:
        # Run analysis for all apps defined in the config
        for app_config in config.APPS_TO_ANALYZE:
            run_analysis_for_app(app_config, start_date_obj, end_date_obj)

if __name__ == "__main__":
    main()
