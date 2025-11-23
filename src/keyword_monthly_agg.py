import ast
from pathlib import Path
from typing import List, Any

import pandas as pd

from logger import AppLogger

logger = AppLogger("[KeywordMonthlyAgg]")


def _parse_keywords_cell(cell: Any) -> List[str]:
  """
  Convert the 'keywords' column read from CSV into a list[str].
  - If it's already a list, return as is.
  - If it's a string "['k1', 'k2']", use literal_eval.
  - Otherwise, fallback to comma split.
  """
  if isinstance(cell, list):
    return cell

  if not isinstance(cell, str) or not cell.strip():
    return []

  text = cell.strip()

  # 1. Try parsing as Python literal list
  try:
    value = ast.literal_eval(text)
    if isinstance(value, list):
      return value
  except Exception:
    pass

  # 2. Fallback: Split by comma
  parts = [p.strip() for p in text.split(",")]
  return [p for p in parts if p]


def build_monthly_keyword_counts(
  input_csv: str = "../datasets/news_keywords_2025.csv",
  output_csv: str = "../datasets/monthly_news_keywords_2025.csv",
) -> pd.DataFrame:
  """
  Generate aggregated CSV: clean_dataset.csv -> (keyword, category, year, month, count).

  Logic:
  - For every keyword in the 'keywords' list of each row,
    accumulate the row's 'article_count' into the (keyword, category, year, month) group.
  """
  logger.info("Starting monthly keyword aggregation process.")

  # 1. Load Data
  try:
    logger.debug(f"Loading cleaned dataset from {input_csv}")
    df = pd.read_csv(input_csv)
  except Exception:
    logger.exception(f"Failed to load dataset from {input_csv}")
    raise

  # 2. Process Dates & Columns
  try:
    logger.debug("Processing dates and numeric columns.")
    
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    # Convert article_count to int
    df["article_count"] = pd.to_numeric(df["article_count"], errors="coerce").fillna(0).astype(int)

    # Check category column
    if "category" not in df.columns:
      raise ValueError("Input CSV must contain 'category' column.")

    # Parse keywords
    df["keywords"] = df["keywords"].apply(_parse_keywords_cell)
  except Exception:
    logger.exception("Error during data processing (date conversion or parsing).")
    raise

  # 3. Explode Keywords & Clean
  try:
    logger.debug("Exploding keywords list into individual rows.")
    
    # Filter only necessary columns
    sub = df[["year", "month", "category", "article_count", "keywords"]].copy()

    # List -> Rows
    sub = sub.explode("keywords")

    # Remove empty keywords
    sub["keywords"] = sub["keywords"].astype(str).str.strip()
    sub = sub[sub["keywords"] != ""]
  except Exception:
    logger.exception("Error during keyword explosion.")
    raise

  # 4. Group & Aggregate
  try:
    logger.debug("Grouping by [keywords, category, year, month].")
    
    grouped = (
      sub
      .groupby(["keywords", "category", "year", "month"], as_index=False)["article_count"]
      .sum()
    )

    grouped = grouped.rename(columns={
      "keywords": "keyword",
      "article_count": "count",
    })

    # Sort: category -> year -> month -> count (descending)
    grouped = grouped.sort_values(
      by=["category", "year", "month", "count"],
      ascending=[True, True, True, False]
    ).reset_index(drop=True)
    
  except Exception:
    logger.exception("Error during grouping and aggregation.")
    raise

  # 5. Save Result
  path = Path(output_csv)
  try:
    logger.debug(f"Saving results to {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(path, index=False, encoding="utf-8-sig")
  except Exception:
    logger.exception(f"Failed to save output CSV to {path}")
    raise

  logger.info(f"Saved monthly keyword counts successfully (rows={len(grouped)}).")

  return grouped