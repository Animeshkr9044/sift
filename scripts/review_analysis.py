import openai
import json
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from fpdf import FPDF
import os

from openai import OpenAI

class ReviewAnalysisAgent:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.seed_topics = [
            "Delivery partner rude",
            "Food stale", 
            "Delivery delay",
            "App crashes",
            "Payment issues",
            "Wrong order",
            "Food quality poor",
            "Customer service bad",
            "App bugs",
            "Pricing high"
        ]
        self.topic_taxonomy = {}
        self.similarity_threshold = 0.75
    
    def extract_topics_from_reviews(self, reviews_batch):
        """Extract topics from a batch of reviews using GPT"""
        
        # Prepare batch for processing (max 20 reviews per API call)
        results = []
        
        for i in tqdm(range(0, len(reviews_batch), 20), desc="Extracting Topics", leave=False):
            batch = reviews_batch[i:i+20]
            
            prompt = f"""
            Analyze these app store reviews for a food delivery app and extract the main topic/issue from each review.
            
            Known topic categories: {self.seed_topics}
            
            For each review, identify:
            1. The main issue/topic (use existing categories if possible, create new if needed)
            2. Whether it's a complaint, request, or compliment
            
            Reviews:
            {json.dumps([{"id": idx, "text": review} for idx, review in enumerate(batch)], indent=2)}
            
            Return a JSON list with format:
            [
                {{
                    "review_id": 0,
                    "topic": "topic_name",
                    "type": "complaint|request|compliment",
                    "confidence": 0.9
                }},
                ...
            ]
            
            Guidelines:
            - Be specific but not overly granular
            - Focus on actionable feedback
            - Group similar issues under same topic name
            - Create new topics only if significantly different from existing ones
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}  # Enforce JSON output
                )
                
                parsed_json = json.loads(response.choices[0].message.content)
                
                # Handle cases where the model wraps the list in a dictionary
                if isinstance(parsed_json, dict) and 'reviews' in parsed_json:
                    batch_results = parsed_json['reviews']
                else:
                    batch_results = parsed_json
                # Link AI results back to the original review text
                for res in batch_results:
                    review_index = res.get("review_id")
                    if review_index is not None and review_index < len(batch):
                        res["review_text"] = batch[review_index]
                results.extend(batch_results)
                
            except Exception as e:
                print(f"Error processing batch {i}: {e}")
                # Enhanced error logging
                try:
                    print("--- API Response Content ---")
                    print(response.choices[0].message.content)
                    print("--------------------------")
                except Exception as log_e:
                    print(f"Could not print response content: {log_e}")
                # Fallback: assign to generic topic
                for idx in range(len(batch)):
                    results.append({
                        "review_id": idx,
                        "topic": "Other issues",
                        "type": "complaint",
                        "confidence": 0.5
                    })
        
        return results
    
    def consolidate_similar_topics(self, extracted_topics):
        """Consolidate similar topics using semantic similarity"""
        
        # Get unique topics from this batch
        unique_topics = list(set([t["topic"] for t in extracted_topics]))
        
        # Compute embeddings for all topics
        topic_embeddings = self.embedding_model.encode(unique_topics)
        
        # Build consolidation mapping
        topic_mapping = {}
        
        for i, topic in enumerate(unique_topics):
            if topic in topic_mapping:
                continue
                
            # Find similar topics
            similarities = cosine_similarity([topic_embeddings[i]], topic_embeddings)[0]
            similar_indices = np.where(similarities > self.similarity_threshold)[0]
            
            # Group similar topics
            similar_topics = [unique_topics[idx] for idx in similar_indices]
            
            # Choose canonical name (shortest, most common, or from seed topics)
            canonical_topic = self.choose_canonical_topic(similar_topics)
            
            # Map all similar topics to canonical
            for similar_topic in similar_topics:
                topic_mapping[similar_topic] = canonical_topic
        
        # Apply mapping to extracted topics
        consolidated_topics = []
        for topic_data in extracted_topics:
            topic_data["topic"] = topic_mapping.get(topic_data["topic"], topic_data["topic"])
            consolidated_topics.append(topic_data)
        
        return consolidated_topics
    
    def choose_canonical_topic(self, similar_topics):
        """Choose the best canonical name for a group of similar topics"""
        
        # Prefer seed topics
        for topic in similar_topics:
            if topic in self.seed_topics:
                return topic
        
        # Prefer shorter, clearer names
        return min(similar_topics, key=len)

    def consolidate_topics_with_llm(self, daily_results):
        """Uses an LLM to perform a final consolidation of topics across all days."""
        print("\n--- Consolidating topics with LLM for final report ---")
        all_topics = set()
        for result in daily_results:
            all_topics.update(result['topic_counts'].keys())
        
        prompt = f"""
        You are an expert data analyst. I have a list of topics from app reviews. Consolidate them into a smaller set of high-level categories.
        Provide a JSON object mapping each original topic to its new, consolidated category.

        Topics to consolidate:
        {json.dumps(list(all_topics), indent=2)}

        Example output format:
        {{
            "Late delivery": "Delivery Issues",
            "Food arrived cold": "Food Quality",
            "App is buggy": "App Performance"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            topic_mapping = json.loads(response.choices[0].message.content)

            # Update all daily results with the new mapping
            for result in daily_results:
                # Update detailed topics first
                for detailed_topic in result['detailed_topics']:
                    old_topic = detailed_topic['topic']
                    if old_topic in topic_mapping:
                        detailed_topic['topic'] = topic_mapping[old_topic]
                
                # Recalculate topic counts based on the new detailed topics
                new_topic_counts = Counter([t['topic'] for t in result['detailed_topics']])
                result['topic_counts'] = dict(new_topic_counts)
            
            print("Topic consolidation complete.")
            return daily_results
        except Exception as e:
            print(f"Error during LLM topic consolidation: {e}")
            # Return original results if consolidation fails
            return daily_results
    
    def generate_trend_report(self, daily_results, target_date, days=30):
        """Generate trend analysis report for the last N days"""
        
        # Calculate date range
        end_date = datetime.strptime(target_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=days-1)
        
        # Create date range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        # Collect all topics
        all_topics = set()
        for result in daily_results:
            all_topics.update(result["topic_counts"].keys())
        
        # Build trend matrix
        trend_data = {}
        for topic in all_topics:
            trend_data[topic] = {}
            for date in date_range:
                # Find counts for this date
                count = 0
                for result in daily_results:
                    if result["date"] == date:
                        count = result["topic_counts"].get(topic, 0)
                        break
                trend_data[topic][date] = count
        
        return {
            "report_date": target_date,
            "date_range": date_range,
            "trends": trend_data,
            "summary": self.generate_summary(trend_data, date_range)
        }
    
    def generate_summary(self, trend_data, date_range):
        """Generate summary insights"""
        
        summary = {
            "top_topics": [],
            "trending_up": [],
            "trending_down": [],
            "new_topics": []
        }
        
        for topic, dates in trend_data.items():
            values = [dates[date] for date in date_range]
            total_mentions = sum(values)
            
            # Top topics by total volume
            summary["top_topics"].append({
                "topic": topic,
                "total_mentions": total_mentions,
                "avg_daily": total_mentions / len(date_range)
            })
            
            # Trending analysis (only works with at least 2 data points)
            mid_point = len(values) // 2
            if mid_point > 0:
                first_half_avg = sum(values[:mid_point]) / mid_point
                second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
                
                # Avoid division by zero if the first half has no mentions
                if first_half_avg > 0:
                    if second_half_avg > first_half_avg * 1.2:  # 20% increase
                        summary["trending_up"].append({
                            "topic": topic,
                            "change": ((second_half_avg - first_half_avg) / first_half_avg) * 100
                        })
                    elif second_half_avg < first_half_avg * 0.8:  # 20% decrease
                        summary["trending_down"].append({
                            "topic": topic,
                            "change": ((first_half_avg - second_half_avg) / first_half_avg) * 100
                        })
        
        # Sort summaries
        summary["top_topics"].sort(key=lambda x: x["total_mentions"], reverse=True)
        summary["trending_up"].sort(key=lambda x: x["change"], reverse=True)
        summary["trending_down"].sort(key=lambda x: x["change"], reverse=True)
        
        return summary


def process_daily_batch_worker(args):
    """Worker function to process a single day's reviews. Runs in a separate process."""
    date, reviews, openai_api_key = args
    # Each worker process needs its own agent instance
    agent = ReviewAnalysisAgent(openai_api_key=openai_api_key)

    # Step 1: Extract topics
    extracted_topics = agent.extract_topics_from_reviews(reviews)
    
    # Step 2: Consolidate similar topics
    consolidated_topics = agent.consolidate_similar_topics(extracted_topics)
    
    # Step 3: Count frequencies
    topic_counts = Counter([t["topic"] for t in consolidated_topics])
    
    return {
        "date": date,
        "topic_counts": dict(topic_counts),
        "total_reviews": len(reviews),
        "topics_found": len(topic_counts),
        "detailed_topics": consolidated_topics
    }

import sqlite3
import re

def preprocess_text(text):
    """Removes emojis and normalizes text to lowercase."""
    if not isinstance(text, str):
        return ""
    # Remove emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub(r"", text)
    # Normalize to lowercase
    text = text.lower()
    return text

def load_your_review_data(db_file='data/reviews.db', table_name='reviews', target_month=None):
    """Loads review data from the SQLite database for a specific month and samples up to 200 reviews per day."""
    print(f"Loading data from {db_file}, table {table_name} for month {target_month}...")
    conn = sqlite3.connect(db_file)
    
    query = f"SELECT SUBSTR(at, 1, 10) as date, content FROM {table_name}"
    if target_month:
        query += f" WHERE strftime('%Y-%m', at) = '{target_month}'"
        
    df = pd.read_sql_query(query, conn)
    conn.close()

    # --- New: Preprocess and filter the data ---
    # 1. Apply text cleaning
    df['content'] = df['content'].apply(preprocess_text)
    
    # 2. Filter out reviews with fewer than 5 words
    df = df[df['content'].str.split().str.len() >= 5]

    daily_reviews = defaultdict(list)
    # Group by date and sample up to 200 reviews from the cleaned data
    for date, group in df.groupby('date'):
        sample_size = min(len(group), 200)
        daily_reviews[date] = group.sample(n=sample_size)['content'].tolist()
    
    print(f"Loaded and sampled reviews for {len(daily_reviews)} days.")
    return daily_reviews

# Usage Example
def main(db_path, output_dir, table_name, target_month="2025-07"):
    # IMPORTANT: Replace "your-api-key" with your actual OpenAI API key
    # The script will not work without a valid key.
    api_key = ""
    if api_key == "your-api-key":
        print("ERROR: Please replace 'your-api-key' with your actual OpenAI API key in the main() function.")
        return
    
    agent = ReviewAnalysisAgent(openai_api_key=api_key)

    # Load data from the specified database for the target month
    daily_reviews = load_your_review_data(
        db_file=db_path, 
        table_name=table_name, 
        target_month=target_month
    )
    
    # Use a ProcessPoolExecutor to run daily analysis in parallel
    tasks = [(date, reviews, api_key) for date, reviews in daily_reviews.items()]
    daily_results = []
    with ProcessPoolExecutor() as executor:
        # The `tqdm` wrapper will show a progress bar for the parallel tasks
        results_iterator = executor.map(process_daily_batch_worker, tasks)
        daily_results = list(tqdm(results_iterator, total=len(tasks), desc="Processing Daily Reviews"))
    
    if not daily_results:
        print(f"No reviews found for {target_month}. Exiting.")
        return

    # Sort results by date to ensure correct processing order
    daily_results.sort(key=lambda x: x['date'])

    # --- New: Perform final topic consolidation using LLM ---
    consolidated_results = agent.consolidate_topics_with_llm(daily_results)

    # Generate trend report for the full month using consolidated data
    last_day_of_month = consolidated_results[-1]['date']
    trend_report = agent.generate_trend_report(consolidated_results, last_day_of_month, days=len(consolidated_results))
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON report
    report_file = os.path.join(output_dir, f"trend_report_{target_month}.json")
    with open(report_file, "w") as f:
        json.dump(trend_report, f, indent=2)
    print(f"\nJSON trend report saved to {report_file}")

    # Create and save the detailed CSV report
    all_detailed_topics = []
    # Use the consolidated results for the CSV report
    for result in consolidated_results:
        all_detailed_topics.extend(result.get('detailed_topics', []))
    
    if all_detailed_topics:
        df_details = pd.DataFrame(all_detailed_topics)
        df_details = df_details[['topic', 'review_text']]
        csv_output_file = os.path.join(output_dir, f"topic_review_details_{target_month}.csv")
        df_details.to_csv(csv_output_file, index=False)
        print(f"Detailed topic-review CSV saved to {csv_output_file}")

    # Generate the PDF report
    pdf_output_file = os.path.join(output_dir, f"trend_report_{target_month}.pdf")
    generate_pdf_report(trend_report, pdf_output_file)

    # Display trend table in console
    display_trend_table(trend_report)

def display_trend_table(trend_report):
    """Display trend data as a table"""
    
    trends = trend_report["trends"]
    date_range = trend_report["date_range"]
    
    # Create DataFrame for easy display
    df_data = {}
    for topic, dates in trends.items():
        df_data[topic] = [dates[date] for date in date_range]
    
    df = pd.DataFrame(df_data, index=date_range).T
    
    print("\n=== TREND ANALYSIS REPORT ===")
    print(f"Report Date: {trend_report['report_date']}")
    print(f"Date Range: {date_range[0]} to {date_range[-1]}")
    print("\nTrend Table:")
    print(df.to_string())
    
    # Display summary
    summary = trend_report["summary"]
    print(f"\n=== TOP TOPICS ===")
    for item in summary["top_topics"][:5]:
        print(f"{item['topic']}: {item['total_mentions']} total mentions")
    
    print(f"\n=== TRENDING UP ===")
    for item in summary["trending_up"][:3]:
        print(f"{item['topic']}: +{item['change']:.1f}% increase")

def generate_pdf_report(trend_report, output_filename):
    """Generates a PDF report with a trend table in landscape mode."""
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)

    # Title
    report_date = trend_report['report_date']
    pdf.cell(0, 10, f'Review Topic Trend Report - {report_date}', align='C')
    pdf.ln(20)

    # Table Header
    pdf.set_font("Helvetica", "B", 8)
    date_range = trend_report['date_range']
    num_dates = len(date_range)
    topic_col_width = 60
    date_col_width = (pdf.w - 2 * pdf.l_margin - topic_col_width) / num_dates

    with pdf.table(col_widths=(topic_col_width,) + (date_col_width,) * num_dates, text_align="CENTER") as table:
        header_row = table.row()
        header_row.cell("Topic")
        for date in date_range:
            day_str = datetime.strptime(date, '%Y-%m-%d').strftime('%b %d')
            header_row.cell(day_str)

        # Table Rows
        for topic, date_counts in trend_report['trends'].items():
            row = table.row()
            display_topic = (topic[:35] + '...') if len(topic) > 35 else topic
            row.cell(display_topic, align="LEFT")
            for date in date_range:
                count = date_counts.get(date, 0)
                row.cell(str(count))

    pdf.output(output_filename)
    print(f"PDF report saved to {output_filename}")

if __name__ == "__main__":
    # This block is now intended for single runs or testing.
    # The main execution will be handled by `run_all_analyses.py`.
    print("Running a single analysis for Swiggy...")
    main(db_path='data/reviews.db', output_dir='swiggy_report', table_name='reviews')
