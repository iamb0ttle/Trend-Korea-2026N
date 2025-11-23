from pathlib import Path
from typing import Dict, Union

import pandas as pd

from logger import AppLogger

logger = AppLogger("[AnalysisTables]")


def load_keyword_monthly_counts(path: str = "../preprocessed/keyword_monthly_counts.csv") -> pd.DataFrame:
  """
  Load the monthly keyword count CSV file.
  """
  logger.info(f"Loading keyword monthly counts from {path}")
  
  try:
    df = pd.read_csv(path)
    logger.debug(f"Loaded {len(df)} rows.")
    return df
  except Exception:
    logger.exception(f"Failed to load CSV from {path}")
    raise


def build_wordcloud_table(
  df: pd.DataFrame,
  output: str = "../preprocessed/wordcloud_top_keywords.csv",
  top_n: int = 100
) -> pd.DataFrame:
  """
  Sum total keyword counts -> Extract Top N (For WordCloud).
  """
  logger.info("Building wordcloud table (calculating total keyword frequency).")

  # 1. Aggregate & Sort
  try:
    logger.debug(f"Aggregating counts by keyword and selecting top {top_n}.")
    
    wc = (
      df.groupby("keyword")["count"]
      .sum()
      .sort_values(ascending=False)
      .reset_index()
    )
    wc_top = wc.head(top_n)
  except Exception:
    logger.exception("Error during aggregation for wordcloud.")
    raise

  # 2. Save to CSV
  try:
    path_obj = Path(output)
    logger.debug(f"Saving wordcloud dataset to {path_obj}")
    
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    wc_top.to_csv(path_obj, index=False, encoding="utf-8-sig")
    
    logger.info(f"Saved wordcloud dataset -> {output} (rows={len(wc_top)})")
  except Exception:
    logger.exception(f"Failed to save wordcloud CSV to {output}")
    raise

  return wc_top


def build_top10_monthly_timeseries(
  df: pd.DataFrame,
  output: str = "../preprocessed/top10_monthly_timeseries.csv",
  top_n: int = 10
) -> pd.DataFrame:
  """
  Select Top 10 keywords by total count -> Create monthly time series data.
  Columns: year, month, keyword, count
  """
  logger.info("Building Top10 keyword monthly timeseries.")

  # 1. Identify Top N Keywords
  try:
    logger.debug(f"Identifying top {top_n} keywords.")
    
    top10_keywords = (
      df.groupby("keyword")["count"]
      .sum()
      .sort_values(ascending=False)
      .head(top_n)
      .index.tolist()
    )
    logger.info(f"Selected Top{top_n} keywords: {top10_keywords}")
  except Exception:
    logger.exception("Error identifying top keywords.")
    raise

  # 2. Filter & Sort Data
  try:
    logger.debug("Filtering original dataframe for top keywords.")
    
    sub = df[df["keyword"].isin(top10_keywords)].copy()
    sub = sub.sort_values(["keyword", "year", "month"])
  except Exception:
    logger.exception("Error filtering/sorting timeseries data.")
    raise

  # 3. Save to CSV
  try:
    path_obj = Path(output)
    logger.debug(f"Saving timeseries dataset to {path_obj}")
    
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    sub.to_csv(path_obj, index=False, encoding="utf-8-sig")
    
    logger.info(f"Saved top10 timeseries dataset -> {output} (rows={len(sub)})")
  except Exception:
    logger.exception(f"Failed to save timeseries CSV to {output}")
    raise

  return sub


def build_economy_top10_table(
  df: pd.DataFrame,
  output: str = "../preprocessed/economy_top10_keywords.csv",
  top_n: int = 10
) -> pd.DataFrame:
  """
  Extract Top 10 keywords for 'economy' category only.
  """
  logger.info("Building Economy Top10 keyword table.")

  # 1. Filter & Aggregate
  try:
    logger.debug("Filtering for 'economy' category and aggregating.")
    
    eco = df[df["category"] == "economy"].copy()

    eco_top = (
      eco.groupby("keyword")["count"]
      .sum()
      .sort_values(ascending=False)
      .head(top_n)
      .reset_index()
    )
  except Exception:
    logger.exception("Error processing economy data.")
    raise

  # 2. Save to CSV
  try:
    path_obj = Path(output)
    logger.debug(f"Saving economy top10 dataset to {path_obj}")
    
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    eco_top.to_csv(path_obj, index=False, encoding="utf-8-sig")
    
    logger.info(f"Saved economy top10 dataset -> {output} (rows={len(eco_top)})")
  except Exception:
    logger.exception(f"Failed to save economy CSV to {output}")
    raise

  return eco_top


def run_all_analysis(input_csv: str = "../preprocessed/keyword_monthly_counts.csv") -> Dict[str, pd.DataFrame]:
  """
  Execute generation of 3 analysis tables.
  """
  logger.info("Starting all analysis tasks.")
  
  try:
    # 1. Load Data
    df = load_keyword_monthly_counts(input_csv)

    # 2. Build Tables
    wc = build_wordcloud_table(df)
    ts = build_top10_monthly_timeseries(df)
    eco = build_economy_top10_table(df)

    logger.info("All analysis tasks completed successfully.")
    
    return {
      "wordcloud": wc,
      "timeseries": ts,
      "economy_top10": eco,
    }
  except Exception:
    logger.exception("An error occurred during the analysis pipeline.")
    raise