from scripts.review_analysis import main as run_analysis

def run_all():
    """
    Orchestrates the review analysis for multiple datasets (Swiggy, Zomato, Blinkit).
    """
    
    # Define the analysis tasks
    analysis_tasks = [
        {
            "name": "Zomato",
            "db_path": "data/zomato_reviews.db",
            "output_dir": "zomato_report",
            "table_name": "zomato_reviews"
        },
        {
            "name": "Blinkit",
            "db_path": "data/blinkit_reviews.db",
            "output_dir": "blinkit_report",
            "table_name": "blinkit_reviews"
        }
    ]
    
    # Run the analysis for each task
    for task in analysis_tasks:
        print(f"\n{'='*20} Starting Analysis for {task['name']} {'='*20}\n")
        try:
            run_analysis(
                db_path=task["db_path"],
                output_dir=task["output_dir"],
                table_name=task["table_name"]
            )
            print(f"\n{'='*20} Finished Analysis for {task['name']} {'='*20}\n")
        except Exception as e:
            print(f"\n{'!'*20} An error occurred during the analysis for {task['name']} {'!'*20}")
            print(f"Error: {e}")
            print(f"{'!'*60}\n")

if __name__ == "__main__":
    run_all()
