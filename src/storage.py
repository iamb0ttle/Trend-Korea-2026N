import csv
from pathlib import Path
from typing import List, Dict, Any

from logger import AppLogger

logger = AppLogger("[Storage]")

def save_news_rows_to_csv(rows: List[Dict[str, Any]], filepath: str) -> None:
  """
  Save crawled news rows (list[dict]) to a CSV file.
  
  - rows example: Return value from crawler.collect_weekly_news_*
  - filepath example: "data/total_news_2025.csv"
  """
  if not rows:
    logger.warning("No rows to save. CSV will not be created.")
    return

  path = Path(filepath)
  
  # CSV Column Definition
  fieldnames = ["date", "category", "title", "article_count"]

  logger.info(f"Saving process started. Target rows: {len(rows)}, Path: {path}")

  # 1. Prepare Directory
  try:
    logger.debug(f"Creating parent directory: {path.parent}")
    path.parent.mkdir(parents=True, exist_ok=True)
  except Exception:
    logger.exception(f"Failed to create directory: {path.parent}")
    raise

  # 2. Write CSV File
  try:
    logger.debug("Opening file and writing data.")
    
    with path.open("w", newline="", encoding="utf-8-sig") as f:
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()

      for row in rows:
        writer.writerow({
          "date": row.get("date"),
          "category": row.get("category"),
          "title": row.get("title"),
          "article_count": row.get("article_count"),
        })
        
    logger.info("Data writing completed.")
  except Exception:
    logger.exception(f"Failed to write CSV file: {path}")
    raise

  logger.info(f"CSV saved successfully: {path}")