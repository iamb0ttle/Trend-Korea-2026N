[**English**](/README.md) | [한국어](/README.ko.md) 

# Trend Korea 2026N

![Python](https://img.shields.io/badge/python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-managed-purple?style=flat-square)
![Selenium](https://img.shields.io/badge/selenium-43B02A?style=flat-square&logo=selenium&logoColor=white)
![Status](https://img.shields.io/badge/status-active-success?style=flat-square)

**Trend Korea 2026N** is a quantitative analysis pipeline designed to predict South Korea's 2026 societal trends by analyzing public discourse data from 2025.

Unlike simple keyword counters, this project implements a **weighted frequency model** based on weekly issue clustering from [BIGKINDS](https://www.bigkinds.or.kr/), enabling the detection of high-impact societal signals over surface-level noise.

---

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Execution Pipeline](#execution-pipeline)
- [Result](#result)

---

## Project Overview

This framework automates the end-to-end process of data acquisition, natural language processing, and trend visualization. It specifically focuses on "Weekly Issues" (aggregations of news clusters) to filter out trivial articles and focus on topics with significant media coverage.

### Core Features
* **Automated Data Collection**: Selenium-based crawler tailored for BIGKINDS' interactive UI (bypassing standard date-pickers).
* **NLP Preprocessing**: Text normalization and morphological analysis using `Komoran` (specialized for Korean syntax).
* **Weighted Aggregation**: Calculates keyword impact scores by multiplying term frequency with the associated `article_count` of the news cluster.
* **Visualization**: Generates Wordclouds and Time-series analysis charts to track keyword lifecycle.

---

## Project Structure

```bash
Trend-Korea-2026N/
├── src/
│   ├── main.py                  # Application entry point / Orchestrator
│   ├── browser_client.py        # Selenium WebDriver singleton & auth handler
│   ├── crawler.py               # Weekly issue scraping logic
│   ├── data_processing.py       # NLP pipeline (Cleaning -> Morph analysis)
│   ├── keyword_monthly_agg.py   # Monthly weighted frequency calculation
│   ├── analysis_tables.py       # Data structuring & statistical summary
│   ├── visualization.py         # Matplotlib/Seaborn visualization engines
│   ├── storage.py               # File I/O & directory management
│   ├── logger.py                # Centralized logging configuration
│   └── utils.py                 # Date handling & helper functions
├── datasets/                    # Raw data storage (CSV)
├── preprocessed/                # Cleaned & Tokenized datasets
├── visualizations/              # Output artifacts (PNG/Charts)
├── stopwords/                   # Stopwords for Korean News data
├── requirements.txt             # Dependency list
└── .env                         # Configuration (Credentials)
```

-----

## Installation & Setup

### Prerequisites

  * Python 3.13+
  * Google Chrome (Latest version)
  * `uv` package manager (recommended) or standard `pip`

### Environment Configuration

1.  Clone the repository:
    ```bash
    git clone https://github.com/iamb0ttle/Trend-Korea-2026N.git
    ```
2.  Install dependencies:
    ```bash
    uv venv
    uv pip install -r requirements.txt
    ```
3.  Create a `.env` file in the root directory:
    ```ini
    BIGKINDS_ID=your_user_id
    BIGKINDS_PW=your_secure_password
    ```

-----

## Execution Pipeline

The pipeline is designed to be run sequentially. You can execute the modules via Python scripts.

**1. Data Crawling**
Collects weekly top 10 issues for designated categories.

```python
from src.crawler import collect_weekly_news_total, collect_weekly_news_economy
collect_weekly_news_total()
collect_weekly_news_economy()
```

**2. Preprocessing**
Cleans raw text and extracts nouns using the Komoran tokenizer.

```python
from src.preprocessing import preprocess_all
preprocess_all()
```

**3. Aggregation**
Applies the weighted scoring model to generate monthly trend data.

```python
from src.aggregation import create_monthly_keyword_frequency
create_monthly_keyword_frequency()
```

**4. Visualization**
Renders analysis results into the `/visualization` directory.

```python
from src.visualization import run_all_visualizations
run_all_visualizations()
```

-----

## Result

### Economy - Top 10 Keywords
![barchart_economy_top10 imaage](/visualizations/barchart_economy_top10.png)
The bar chart shows the most influential economic keywords in 2025, weighted by total article volume.</br>
현대차(Hyundai Motor) overwhelmingly leads the ranking, followed by 관세(tariffs) and LG, indicating strong attention on corporate performance and trade policy issues. </br>
Mid-tier keywords such as 미국(United States), 트럼프(Trump), AI, and 반도체(semiconductors) highlight the impact of global politics and tech-industry dynamics on Korea’s economic narrative. </br>
Overall, the distribution reflects a mix of major corporations, geopolitical factors, and emerging technologies shaping Korea’s economic discourse.</br>

### Top 10 Keywords - Monthly Trends
![lineplot_top10_trend imaage](/visualizations/lineplot_top10_trend.png)
Similarly, The monthly trend chart reveals clear event-driven spikes in public attention. 산불(wildfires) shows a dramatic surge in March, reflecting a major nationwide wildfire incident that dominated the news cycle. </br>
트럼프(Trump) and 관세(tariffs) rise sharply during periods of intensified U.S.–Korea trade tensions, highlighting the sensitivity of Korean economic discourse to global political shifts. </br>
Keywords like 윤석열(Yoon Suk-yeol) and 이재명(Lee Jae-myung) maintain steady visibility, illustrating the persistent influence of political leadership in shaping monthly media narratives. </br>

### World Cloud
![wordcloud_total imaage](/visualizations/wordcloud_total.png)
The word cloud highlights the dominant topics that shaped Korean public discourse throughout 2025. </br>
Political figures such as 대통령(President), 이재명(Lee Jae-myung), 윤석열(Yoon Suk-yeol), and 트럼프(Trump) appear prominently, showing how leadership and geopolitical events continued to drive national conversations. </br>
Economic and policy-related keywords like 탄핵(impeachment), 관세(tariffs), 반도체(semiconductors), and 대행(acting authority) indicate strong interest in governance, trade disputes, and tech industries. </br>
Overall, the cloud reflects a year defined by political polarization, global economic pressures, and emerging technological themes. </br>

-----

## License & Disclaimer

**Data Rights**: The metadata and article content analyzed in this project belong to **BIGKINDS (Korea Press Foundation)**.
**Usage**: This project is for **educational and research purposes only**. Commercial use of the crawled data is strictly prohibited without permission from the original copyright holders.

MIT License © 2025 Byeonghyeon Na
