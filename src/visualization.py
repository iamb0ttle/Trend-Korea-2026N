from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
from matplotlib.ticker import MultipleLocator

from logger import AppLogger

logger = AppLogger("[Visualization]")

# Global Matplotlib Settings
plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False


def generate_wordcloud(
  input_csv: str = "../preprocessed/wordcloud_top_keywords.csv",
  output_path: str = "../visualizations/wordcloud_total.png",
  font_path: Optional[str] = None,
) -> None:
  """
  Generate a WordCloud based on total top keywords.
  """
  logger.info(f"Generating WordCloud. Input: {input_csv}")

  try:
    # 1. Load Data
    logger.debug(f"Loading data from {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Convert to dictionary {keyword: count}
    freqs = {row["keyword"]: int(row["count"]) for _, row in df.iterrows()}
    logger.debug(f"Loaded {len(freqs)} keywords for WordCloud.")

    # 2. Generate WordCloud Object
    wc = WordCloud(
      width=1600,
      height=900,
      background_color="white",
      font_path=font_path,
    ).generate_from_frequencies(freqs)

    # 3. Plot & Save
    path_obj = Path(output_path)
    logger.debug(f"Saving WordCloud image to {path_obj}")
    
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 7))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()

    plt.savefig(output_path, dpi=200)
    plt.close()
    
    logger.info(f"Saved WordCloud -> {output_path}")

  except Exception:
    logger.exception("Failed to generate WordCloud.")
    raise


def generate_lineplot(
  input_csv: str = "../preprocessed/top10_monthly_timeseries.csv",
  output_path: str = "../visualizations/lineplot_top10_trend.png",
) -> None:
  """
  Generate a line plot for the monthly trend of Top 10 keywords.
  """
  logger.info(f"Generating Line Plot. Input: {input_csv}")

  try:
    # 1. Load & Preprocess Data
    logger.debug(f"Loading timeseries data from {input_csv}")
    df = pd.read_csv(input_csv)

    df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)

    # 2. Plotting
    logger.debug("Plotting time series data.")
    
    plt.figure(figsize=(12, 7))
    plt.grid(True)

    unique_keywords = df["keyword"].unique()
    for keyword in unique_keywords:
      sub = df[df["keyword"] == keyword].copy()
      sub = sub.sort_values(["year", "month"])
      plt.plot(
        sub["year_month"],
        sub["count"],
        marker="o",
        label=keyword
      )
      
    ax = plt.gca()
    ax.yaxis.set_major_locator(MultipleLocator(500))

    plt.xticks(rotation=45)
    plt.xlabel("Year-Month")
    plt.ylabel("Weighted Frequency (article_count sum)")
    plt.title("Top 10 Keywords — Monthly Trend")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
    plt.tight_layout()

    # 3. Save
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=200)
    plt.close()

    logger.info(f"Saved Line Plot -> {output_path}")

  except Exception:
    logger.exception("Failed to generate Line Plot.")
    raise


def generate_barchart(
  input_csv: str = "../preprocessed/economy_top10_keywords.csv",
  output_path: str = "../visualizations/barchart_economy_top10.png",
) -> None:
  """
  Generate a horizontal bar chart for Economy Top 10 keywords.
  """
  logger.info(f"Generating Bar Chart. Input: {input_csv}")

  try:
    # 1. Load Data
    logger.debug(f"Loading economy top10 data from {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Sort for display
    df = df.sort_values("count", ascending=True)

    # 2. Plotting
    logger.debug("Plotting bar chart.")
    
    plt.figure(figsize=(10, 6))
    plt.barh(df["keyword"], df["count"])
    plt.xlabel("Weighted Frequency (article_count sum)")
    plt.title("Economy — Top 10 Keywords")
    plt.tight_layout()

    # 3. Save
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=200)
    plt.close()

    logger.info(f"Saved Bar Chart -> {output_path}")

  except Exception:
    logger.exception("Failed to generate Bar Chart.")
    raise


def run_all_visualizations(
  wordcloud_csv: str = "../preprocessed/wordcloud_top_keywords.csv",
  timeseries_csv: str = "../preprocessed/top10_monthly_timeseries.csv",
  economy_csv: str = "../preprocessed/economy_top10_keywords.csv",
  font_path: Optional[str] = None,
) -> None:
  """
  Execute all visualization tasks sequentially.
  """
  logger.info("Starting all visualization tasks.")

  try:
    generate_wordcloud(
      input_csv=wordcloud_csv,
      output_path="../visualizations/wordcloud_total.png",
      font_path=font_path,
    )

    generate_lineplot(
      input_csv=timeseries_csv,
      output_path="../visualizations/lineplot_top10_trend.png",
    )

    generate_barchart(
      input_csv=economy_csv,
      output_path="../visualizations/barchart_economy_top10.png",
    )
    
    logger.info("All visualization tasks completed successfully.")
    
  except Exception:
    logger.exception("An error occurred during the visualization pipeline.")
    # Depending on requirements, we might want to raise here or let it finish partially.
    raise