# pulse_engine/reporting/generator.py

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF

def generate_trend_report(daily_results, target_date, days=30):
    """Generate trend analysis report for the last N days"""
    end_date = datetime.strptime(target_date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=days-1)
    date_range = [d.strftime("%Y-%m-%d") for d in pd.date_range(start_date, end_date)]
    
    all_topics = set()
    for result in daily_results:
        all_topics.update(result['topic_counts'].keys())

    trends = {topic: {date: 0 for date in date_range} for topic in all_topics}
    for result in daily_results:
        date = result['date']
        if date in trends[list(trends.keys())[0]]:
            for topic, count in result['topic_counts'].items():
                if topic in trends:
                    trends[topic][date] = count
    
    summary = {
        'top_topics': sorted([{'topic': t, 'total_mentions': sum(trends[t].values())} for t in trends], key=lambda x: x['total_mentions'], reverse=True)[:5],
        'trending_up': []
    }

    return {
        'report_date': target_date,
        'date_range': date_range,
        'trends': trends,
        'summary': summary
    }

def save_reports(trend_report, detailed_results, output_dir, date_range_str):
    """Saves the JSON, CSV, and PDF reports."""
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON report
    json_path = os.path.join(output_dir, f"trend_report_{date_range_str}.json")
    with open(json_path, 'w') as f:
        json.dump(trend_report, f, indent=4)
    print(f"JSON trend report saved to {json_path}")

    # Save detailed CSV report
    csv_path = os.path.join(output_dir, f"topic_review_details_{date_range_str}.csv")
    all_topic_details = []
    for day_result in detailed_results:
        for topic_detail in day_result['detailed_topics']:
            all_topic_details.append({
                'date': day_result['date'],
                'topic': topic_detail['topic'],
                'review': topic_detail['review']
            })
    pd.DataFrame(all_topic_details).to_csv(csv_path, index=False)
    print(f"Detailed topic-review CSV saved to {csv_path}")

    # Generate and save the PDF report
    pdf_path = os.path.join(output_dir, f"trend_report_{date_range_str}.pdf")
    _generate_pdf_report(trend_report, pdf_path)
    print(f"PDF report saved to {pdf_path}")
    _display_trend_table(trend_report)

def _generate_pdf_report(trend_report, output_filename):
    """Generates a PDF report with a trend table in landscape mode."""
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    report_date = trend_report['report_date']
    pdf.cell(0, 10, f'Review Topic Trend Report - {report_date}', align='C')
    pdf.ln(20)
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

        for topic, date_counts in trend_report['trends'].items():
            row = table.row()
            display_topic = (topic[:35] + '...') if len(topic) > 35 else topic
            row.cell(display_topic, align="LEFT")
            for date in date_range:
                count = date_counts.get(date, 0)
                row.cell(str(count))
    pdf.output(output_filename)

def _display_trend_table(trend_report):
    """Display trend data as a table in the console."""
    trends = trend_report["trends"]
    date_range = trend_report["date_range"]
    df = pd.DataFrame(trends).reindex(date_range, axis='columns', fill_value=0)
    print("\nTrend Table:")
    print(df.transpose())
    summary = trend_report['summary']
    print("\n=== TOP TOPICS ===")
    for item in summary["top_topics"]:
        print(f"{item['topic']}: {item['total_mentions']} total mentions")
