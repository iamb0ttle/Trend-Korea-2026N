import re
from pathlib import Path
from typing import List, Set

import pandas as pd
from konlpy.tag import Komoran

from logger import AppLogger
from utils import load_stopwords

logger = AppLogger("[DataProcessing]")

komoran = Komoran()

STOPWORDS = load_stopwords()


def _load_raw_datasets(
  total_csv_path: str,
  economy_csv_path: str,
) -> pd.DataFrame:
  """
  Load total and economy CSV files and concatenate them into a single DataFrame.
  - Columns: date, category, title, article_count
  """
  logger.info("Loading raw datasets process started.")

  try:
    # 1. Load Total CSV
    logger.debug(f"Loading total CSV from {total_csv_path}")
    df_total = pd.read_csv(total_csv_path)

    # 2. Load Economy CSV
    logger.debug(f"Loading economy CSV from {economy_csv_path}")
    df_econ = pd.read_csv(economy_csv_path)

    # 3. Concatenate DataFrames
    logger.debug("Concatenating total and economy dataframes.")
    df = pd.concat([df_total, df_econ], ignore_index=True)
    
    logger.info(f"Datasets loaded successfully. Total rows: {len(df)}")
    return df

  except Exception:
    logger.exception("Failed to load or concatenate datasets.")
    raise


def _clean_text(text: str) -> str:
  """
  Refine news titles using regular expressions.
  - Remove special characters
  - Normalize whitespace
  """
  if not isinstance(text, str):
    return ""

  # Remove characters except Korean, English, Numbers, and Whitespace
  text = re.sub(r"[^가-힣0-9A-Za-z\s]", " ", text)

  # Replace multiple spaces with a single space
  text = re.sub(r"\s+", " ", text)

  return text.strip()


def _extract_keywords(text: str, stopwords: Set[str] = STOPWORDS) -> List[str]:
  """
  Extract keywords from text using Komoran (Korean Nouns) and Regex (English).
  """
  if not isinstance(text, str) or not text.strip():
    return []

  cleaned = _clean_text(text)
  
  try:
    # 1. Extract Korean Nouns
    ko_nouns = komoran.nouns(cleaned)

    # 2. Extract English Tokens (Length >= 2)
    en_tokens = re.findall(r"[A-Za-z]{2,}", cleaned)
    # Normalize to uppercase (AI, ESG, CPI, etc.)
    en_tokens = [w.upper() for w in en_tokens]

    # 3. Merge & Deduplicate (Preserving Order)
    merged = ko_nouns + en_tokens
    merged = list(dict.fromkeys(merged))

    # 4. Remove Stopwords & Single-character Tokens
    keywords = [
      t for t in merged
      if t not in stopwords and len(t) > 1
    ]
    
    return keywords

  except Exception:
    logger.warning(f"Failed to extract keywords from text: {text[:20]}...")
    return []


def preprocess_news_dataset(
  total_csv_path: str,
  economy_csv_path: str,
  output_csv_path: str = "data/clean_dataset.csv",
) -> pd.DataFrame:
  """
  Full Preprocessing Pipeline:
  - Load CSVs
  - Drop NA & Duplicates
  - Clean Text
  - Extract Keywords (Komoran + Stopwords)
  - Save to 'clean_dataset.csv'
  """
  logger.info("Starting preprocessing pipeline.")

  # 1. Load Data
  try:
    df = _load_raw_datasets(total_csv_path, economy_csv_path)
  except Exception:
    # _load_raw_datasets already logs the exception
    return pd.DataFrame()

  # 2. Data Cleaning (Drop NA & Duplicates)
  try:
    logger.debug("Dropping rows with missing date/category/title.")
    df = df.dropna(subset=["date", "category", "title"])

    before_dup = len(df)
    logger.debug("Dropping duplicates based on date, category, and title.")
    df = df.drop_duplicates(subset=["date", "category", "title"])
    after_dup = len(df)
    
    logger.info(f"Dropped duplicates: {before_dup - after_dup} rows.")
  except Exception:
    logger.exception("Error during data cleaning (dropna/duplicates).")
    raise

  # 3. NLP Processing (Text Cleaning & Keyword Extraction)
  try:
    logger.info("Cleaning titles and extracting keywords with Komoran.")

    # Create temporary clean_title column
    df["clean_title"] = df["title"].astype(str).apply(_clean_text)

    # Extract keywords
    df["keywords"] = df["clean_title"].apply(_extract_keywords)

    # Cast article_count to numeric
    if "article_count" in df.columns:
      df["article_count"] = pd.to_numeric(df["article_count"], errors="coerce")
      
  except Exception:
    logger.exception("Error during NLP processing.")
    raise

  # 4. Save Processed Data
  path = Path(output_csv_path)
  
  try:
    logger.debug(f"Creating directory: {path.parent}")
    path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving cleaned dataset to {path}")
    df.to_csv(path, index=False, encoding="utf-8-sig")
  except Exception:
    logger.exception(f"Failed to save cleaned dataset to {path}.")
    raise

  logger.info(f"Preprocessing done. Final rows: {len(df)}")
  return df