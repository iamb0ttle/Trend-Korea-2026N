import argparse
from datetime import date

from browser_client import BrowserClient
from crawler import collect_weekly_news_total, collect_weekly_news_economy
from data_processing import preprocess_news_dataset
from keyword_monthly_agg import build_monthly_keyword_counts
from logger import AppLogger
from storage import save_news_rows_to_csv
from analysis_tables import run_all_analysis
from visualization import run_all_visualizations

# File Path Constants
TOTAL_NEWS_PATH = "../datasets/total_news_2025.csv"
ECONOMY_NEWS_PATH = "../datasets/economy_news_2025.csv"
KEYWORDS_PATH = "../datasets/news_keywords_2025.csv"
MONTHLY_KEYWORDS_PATH = "../datasets/monthly_news_keywords_2025.csv"
FONT_PATH = "../fonts/Pretendard-Regular.otf"

logger = AppLogger("[Main]")

def run_crawler():
  """
  Execute the crawling process and save the data.
  """
  logger.info("Starting crawling process...")
  client = BrowserClient()

  total_rows = []
  economy_rows = []

  try:
    client.login()

    start = date(2025, 1, 1)
    end = date(2025, 11, 21)

    # 1. Collect Total News
    logger.info(f"Collecting [Total] news from {start} to {end}...")
    total_rows = collect_weekly_news_total(client, start, end)
    
    # 2. Collect Economy News
    logger.info(f"Collecting [Economy] news from {start} to {end}...")
    economy_rows = collect_weekly_news_economy(client, start, end)

  except Exception:
    logger.exception("An error occurred during the crawling process.")
  finally:
    client.close()

  # 3. Save Data
  if total_rows:
    try:
      save_news_rows_to_csv(total_rows, TOTAL_NEWS_PATH)
      logger.info(f"Total news saved: {TOTAL_NEWS_PATH}")
    except Exception:
      logger.exception("Failed to save total news CSV.")
  
  if economy_rows:
    try:
      save_news_rows_to_csv(economy_rows, ECONOMY_NEWS_PATH)
      logger.info(f"Economy news saved: {ECONOMY_NEWS_PATH}")
    except Exception:
      logger.exception("Failed to save economy news CSV.")


def run_preprocessing():
  """
  Load saved CSV files and execute preprocessing.
  """
  logger.info("Starting data preprocessing process...")
  
  try:
    # The preprocess_news_dataset function handles file loading and error logging internally.
    preprocess_news_dataset(TOTAL_NEWS_PATH, ECONOMY_NEWS_PATH, KEYWORDS_PATH)
    build_monthly_keyword_counts(KEYWORDS_PATH, MONTHLY_KEYWORDS_PATH)
    logger.info(f"Preprocessing completed. Result saved to: {KEYWORDS_PATH}")
  except Exception:
    logger.exception("An error occurred during the preprocessing step.")
    
def run_analysis_table() -> None:
  """
  Execute the analysis table generation process.
  """
  logger.info("Starting analysis table generation...")

  try:
    # Assuming MONTHLY_KEYWORDS_PATH is defined globally
    run_all_analysis(MONTHLY_KEYWORDS_PATH)
    logger.info("Analysis table generation completed successfully.")
  except Exception:
    logger.exception("Failed during analysis table generation.")
    

def run_visualizations() -> None:
  """
  Execute the visualization generation process.
  """
  logger.info("Starting visualization process...")

  try:
    # Assuming FONT_PATH is defined globally
    run_all_visualizations(font_path=FONT_PATH)
    logger.info("Visualization process completed successfully.")
  except Exception:
    logger.exception("Failed during visualization process.")

def main():
  parser = argparse.ArgumentParser(description="News Crawler & Data Preprocessor")
  
  # --step argument (default: all)
  parser.add_argument(
    "--step", 
    type=str, 
    choices=["crawl", "process", "analysis", "viz", "all"], 
    default="all",
    help="Select step to execute: crawl, process, or all"
  )

  args = parser.parse_args()

  # 1. Crawling Step
  if args.step in ["crawl", "all"]:
    run_crawler()

  # 2. Preprocessing Step
  if args.step in ["process", "all"]:
    run_preprocessing()

  if args.step in ["analysis", "all"]:
    run_analysis_table()
    
  if args.step in ["viz", "all"]:
    run_visualizations()
    
if __name__ == "__main__":
  main()