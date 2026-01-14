from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
from matplotlib.ticker import MultipleLocator
import ast
import seaborn as sns
from itertools import combinations
from collections import Counter

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


def generate_enhanced_lineplot(
  input_csv: str = "../preprocessed/top10_monthly_timeseries.csv",
  output_path: str = "../visualizations/enhanced_lineplot_top10_trend.png",
  anomaly_threshold: float = 0.25
) -> None:
  """
  Generate a line plot with automatic Anomaly Detection and Event Annotation.
  (Indentation: 2 spaces)
  """
  logger.info(f"Generating Enhanced Line Plot. Input: {input_csv}")

  try:
    # 1. 데이터 로드 및 시계열 전처리
    logger.debug(f"Loading timeseries data from {input_csv}")
    df = pd.read_csv(input_csv)
    
    # datetime 변환을 통한 정확한 시계열 정렬
    df["date"] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df = df.sort_values(["keyword", "date"])
    df["year_month"] = df["date"].dt.strftime("%Y-%m")

    # 2. 그래프 설정
    logger.debug("Plotting time series with anomaly detection.")
    plt.figure(figsize=(14, 8))
    plt.grid(True, linestyle="--", alpha=0.5)
    
    unique_keywords = df["keyword"].unique()
    colors = plt.cm.get_cmap('tab10', len(unique_keywords))

    for idx, keyword in enumerate(unique_keywords):
      sub = df[df["keyword"] == keyword].copy()
      
      # 이상치 탐지: 전월 대비 변화율 계산
      sub["prev_count"] = sub["count"].shift(1)
      sub["pct_change"] = (sub["count"] - sub["prev_count"]) / sub["prev_count"]
      
      line, = plt.plot(
        sub["year_month"],
        sub["count"],
        marker="o",
        markersize=4,
        label=keyword,
        color=colors(idx),
        linewidth=2,
        alpha=0.8
      )

      # 이상치 주석(Annotation) 추가
      anomalies = sub[sub["pct_change"] > anomaly_threshold]
      for _, row in anomalies.iterrows():
        # 'headline' 컬럼이 있으면 출력, 없으면 기본 메시지 출력
        label = row.get('headline', f"급증: {row['keyword']}")
        
        plt.annotate(
          label,
          xy=(row["year_month"], row["count"]),
          xytext=(5, 15),
          textcoords='offset points',
          fontsize=8,
          fontweight='bold',
          arrowprops=dict(arrowstyle='->', color=line.get_color(), lw=1),
          bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=line.get_color(), alpha=0.8)
        )

    # 3. 레이아웃 및 스타일링
    ax = plt.gca()
    ax.yaxis.set_major_locator(MultipleLocator(500))
    
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Year-Month", fontsize=11)
    plt.ylabel("Weighted Frequency", fontsize=11)
    plt.title("Top 10 Keywords — Monthly Trend (Anomaly Annotated)", fontsize=15, pad=20)
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), title="Keywords")
    plt.tight_layout()

    # 4. 저장
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=250, bbox_inches='tight')
    plt.close()

    logger.info(f"Saved Enhanced Line Plot -> {output_path}")

  except Exception:
    logger.exception("Failed to generate Enhanced Line Plot.")
    raise


def generate_cooccurrence_heatmap(
  input_csv: str = "../datasets/news_keywords_2025.csv",
  output_path: str = "../visualizations/heatmap_keyword_cooccurrence.png"
) -> None:
  """
  TOP 10 경제 키워드가 한 기사에 동시에 등장하는 빈도를 분석하여 히트맵을 생성합니다.
  """
  logger.info(f"Generating Co-occurrence Heatmap. Input: {input_csv}")

  try:
    # 1. 데이터 로드
    df = pd.read_csv(input_csv)
    
    # 2. 분석 대상 TOP 10 키워드 설정
    target_keywords = ["현대차", "관세", "LG", "미국", "트럼프", "AI", "SK", "기아", "대통령", "반도체"]
    
    # 3. 동시 출현 빈도 계산
    # 각 행의 'keywords' 컬럼(문자열)을 실제 리스트로 변환 후 조합 추출
    pair_counts = Counter()
    
    logger.debug("Calculating keyword pairs from articles.")
    for raw_keywords in df['keywords']:
      try:
        # 문자열 형태의 리스트 "['a', 'b']"를 실제 리스트 ['a', 'b']로 변환
        kw_list = ast.literal_eval(raw_keywords)
        
        # 기사 내 키워드 중 target_keywords에 포함된 것만 필터링 (중복 제거)
        found = sorted(list(set([k for k in kw_list if k in target_keywords])))
        
        # 한 기사에 2개 이상의 타겟 키워드가 등장한 경우만 조합 생성
        if len(found) >= 2:
          for pair in combinations(found, 2):
            pair_counts[pair] += 1
        elif len(found) == 1:
          # 자기 자신과의 관계(대각선)를 위해 카운트 (선택 사항)
          pair_counts[(found[0], found[0])] += 1
          
      except (ValueError, SyntaxError):
        continue

    # 4. 행렬(Matrix) 데이터프레임 생성
    matrix = pd.DataFrame(0, index=target_keywords, columns=target_keywords)
    for (k1, k2), count in pair_counts.items():
      matrix.loc[k1, k2] = count
      matrix.loc[k2, k1] = count # 대칭 행렬 설정

    # 5. 시각화
    plt.figure(figsize=(14, 11))
    
    # 가독성을 위해 데이터가 없는 부분은 0으로 표시하고, 
    # 상관관계가 높은 부분을 강조하기 위해 'YlGnBu' 또는 'magma' 컬러맵 사용
    sns.heatmap(
      matrix, 
      annot=True, 
      fmt="d", 
      cmap="YlGnBu", 
      linewidths=0.5,
      cbar_kws={'label': 'Co-occurrence Count (Shared Articles)'}
    )
    
    plt.title("Economic Trends: Keyword Co-occurrence Heatmap", fontsize=18, pad=25)
    plt.xlabel("Keywords", fontsize=12)
    plt.ylabel("Keywords", fontsize=12)
    plt.tight_layout()

    # 6. 저장
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()

    logger.info(f"Saved Co-occurrence Heatmap -> {output_path}")

  except Exception:
    logger.exception("Failed to generate Co-occurrence Heatmap.")
    raise


def run_all_visualizations(
  wordcloud_csv: str = "../preprocessed/wordcloud_top_keywords.csv",
  timeseries_csv: str = "../preprocessed/top10_monthly_timeseries.csv",
  economy_csv: str = "../preprocessed/economy_top10_keywords.csv",
  raw_keywords_csv: str = "../datasets/news_keywords_2025.csv",
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

    generate_enhanced_lineplot(
      input_csv=timeseries_csv,
      output_path="../visualizations/enhanced_lineplot_top10_trend.png"
    )

    generate_cooccurrence_heatmap(
      input_csv=raw_keywords_csv,
      output_path="../visualizations/heatmap_cooccurrence.png"
    )
    
    logger.info("All visualization tasks completed successfully.")
    
  except Exception:
    logger.exception("An error occurred during the visualization pipeline.")
    # Depending on requirements, we might want to raise here or let it finish partially.
    raise