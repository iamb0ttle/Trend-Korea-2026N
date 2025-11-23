[English](/README.md) | [**한국어**](/README-ko.md)

# Trend Korea 2026N

![Trend Korea 2026N Banner](/images/tk2026n-banner.png)

![Python](https://img.shields.io/badge/python-3.14-3776AB?style=flat-square&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-managed-purple?style=flat-square)
![Selenium](https://img.shields.io/badge/selenium-43B02A?style=flat-square&logo=selenium&logoColor=white)
![Status](https://img.shields.io/badge/status-active-success?style=flat-square)

**Trend Korea 2026N**은 2025년의 대중 담론 데이터를 분석하여, 다가올 2026년 대한민국의 사회적 트렌드를 예측하기 위해 설계된 정량적 분석 파이프라인입니다.

단순한 키워드 빈도 측정 방식과 달리, 본 프로젝트는 [BIGKINDS](https://www.bigkinds.or.kr/)의 주간 이슈 클러스터링 데이터를 기반으로 한 **가중치 빈도 모델(Weighted Frequency Model)**을 구현했습니다. 이를 통해 단순한 노이즈를 걸러내고 사회적으로 실질적인 영향력을 가진 신호를 포착합니다.

---

## 📋 목차
- [프로젝트 개요](#프로젝트-개요)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 설정](#설치-및-설정)
- [실행 파이프라인](#실행-파이프라인)
- [분석 결과](#분석-결과)

---

## 프로젝트 개요

이 프레임워크는 데이터 수집부터 자연어 처리(NLP), 트렌드 시각화에 이르는 전 과정을 자동화합니다. 특히 개별 기사가 아닌 뉴스 클러스터의 집합체인 '주간 이슈'에 집중함으로써, 중요도가 낮은 기사들을 필터링하고 미디어의 주목도가 높은 핵심 주제를 선별합니다.

### 핵심 기능
* **자동화된 데이터 수집**: Selenium 기반 크롤러를 통해 BIGKINDS의 동적 UI(날짜 선택기 등)를 우회하여 데이터를 수집합니다.
* **NLP 전처리**: 한국어 구문에 최적화된 `Komoran`을 사용하여 텍스트 정규화 및 형태소 분석을 수행합니다.
* **가중치 집계**: 단순 빈도가 아닌, 뉴스 클러스터의 `article_count`(기사 수)와 키워드 빈도를 곱하여 해당 이슈의 사회적 파급력을 점수화합니다.
* **시각화**: 워드클라우드 및 시계열 차트를 생성하여 키워드의 생애주기와 트렌드 변화를 추적합니다.

---

## 프로젝트 구조

```bash
Trend-Korea-2026N/
├── src/
│   ├── main.py                  # 애플리케이션 진입점 / 오케스트레이터
│   ├── browser_client.py        # Selenium WebDriver 싱글톤 & 인증 핸들러
│   ├── crawler.py               # 주간 이슈 크롤링 로직
│   ├── data_processing.py       # NLP 파이프라인 (정제 -> 형태소 분석)
│   ├── keyword_monthly_agg.py   # 월간 가중치 빈도 계산
│   ├── analysis_tables.py       # 데이터 구조화 및 통계 요약
│   ├── visualization.py         # Matplotlib/Seaborn 시각화 엔진
│   ├── storage.py               # 파일 I/O 및 디렉토리 관리
│   ├── logger.py                # 중앙 로깅 설정
│   └── utils.py                 # 날짜 처리 및 헬퍼 함수
├── datasets/                    # 원본 데이터 저장소 (CSV)
├── preprocessed/                # 정제 및 토큰화된 데이터셋
├── visualizations/              # 생성된 시각화 결과물 (PNG/Charts)
├── stopwords/                   # 뉴스 데이터용 불용어 리스트
├── requirements.txt             # 의존성 패키지 목록
└── .env                         # 환경 설정 (계정 정보)
````

-----

## 설치 및 설정

### 사전 요구 사항

  * Python 3.13 이상
  * Google Chrome (최신 버전)
  * `uv` 패키지 매니저 (권장) 또는 표준 `pip`

### 환경 구성

1.  레포지토리 클론:
    ```bash
    git clone https://github.com/iamb0ttle/Trend-Korea-2026N.git
    ```
2.  의존성 설치:
    ```bash
    uv venv
    uv pip install -r requirements.txt
    ```
3.  루트 디렉토리에 `.env` 파일 생성:
    ```ini
    BIGKINDS_ID=your_user_id
    BIGKINDS_PW=your_secure_password
    ```

-----

## 실행 파이프라인

이 파이프라인은 모듈 단위로 순차 실행되도록 설계되었습니다. Python 스크립트를 통해 각 단계를 실행할 수 있습니다.

**1. 데이터 크롤링**
지정된 카테고리(종합, 경제 등)의 주간 상위 10개 이슈를 수집합니다.

```python
from src.crawler import collect_weekly_news_total, collect_weekly_news_economy
collect_weekly_news_total()
collect_weekly_news_economy()
```

**2. 전처리 (Preprocessing)**
수집된 원문 텍스트를 정제하고 Komoran 토크나이저를 사용해 명사를 추출합니다.

```python
from src.data_processing import preprocess_all
preprocess_all()
```

**3. 집계 및 분석 (Aggregation)**
가중치 점수 모델을 적용하여 월별 트렌드 데이터를 생성합니다.

```python
from src.keyword_monthly_agg import create_monthly_keyword_frequency
create_monthly_keyword_frequency()
```

**4. 시각화 (Visualization)**
분석 결과를 `/visualizations` 디렉토리에 시각화 이미지로 렌더링합니다.

```python
from src.visualization import run_all_visualizations
run_all_visualizations()
```

-----

## 분석 결과

### 경제 분야 Top 10 키워드
![barchart_economy_top10 imaage](/visualizations/barchart_economy_top10.png)
위 막대 차트는 기사 총량을 가중치로 반영하여 산출한 2025년 가장 영향력 있는 경제 키워드를 보여줍니다.<br>
**현대차**가 압도적인 1위를 차지했으며, **관세**와 **LG**가 그 뒤를 이어 기업 실적과 글로벌 무역 정책 이슈에 대한 높은 관심을 나타냅니다.<br>
중위권에는 **미국, 트럼프, AI, 반도체** 등의 키워드가 포진해 있어, 국제 정세와 기술 산업의 역동성이 한국 경제 담론에 미치는 영향을 확인할 수 있습니다.<br>
전반적으로 대기업, 지정학적 요소, 신기술이 2025년 경제 담론을 주도했음을 시사합니다.

### Top 10 키워드 월별 트렌드
![lineplot_top10_trend imaage](/visualizations/lineplot_top10_trend.png)
월별 트렌드 차트는 대중의 관심이 특정 사건(Event-driven)에 따라 어떻게 급증하는지 명확히 보여줍니다.
3월에는 대형 산불 이슈로 인해 **산불** 키워드가 급격히 치솟았습니다.<br>
**트럼프**와 **관세** 키워드는 한미 무역 긴장이 고조되는 시기에 맞춰 동반 상승하는 경향을 보이며, 한국 경제가 글로벌 정치 이슈에 민감하게 반응함을 알 수 있습니다.<br>
반면 **윤석열, 이재명**과 같은 정치적 키워드는 꾸준한 노출 빈도를 유지하며, 정치 리더십이 미디어 서사에서 지속적인 영향력을 행사하고 있음을 보여줍니다.

### 종합 워드클라우드
![wordcloud_total imaage](/visualizations/wordcloud_total.png)
워드클라우드는 2025년 한 해 동안 한국 사회의 담론을 지배했던 핵심 주제들을 시각화한 것입니다.<br>
**대통령, 이재명, 윤석열, 트럼프**와 같은 정치 인물들이 가장 크게 나타나, 리더십과 지정학적 이슈가 국가적 대화를 주도했음을 알 수 있습니다.<br>
또한 **탄핵, 관세, 반도체, 대행**과 같은 경제·정책 관련 키워드들은 거버넌스, 무역 분쟁, 핵심 기술 산업에 대한 대중의 높은 관심을 반영합니다.<br>
종합적으로 볼 때, 2025년은 정치적 양극화, 글로벌 경제 압박, 그리고 기술적 전환이 맞물린 해였음을 시각적으로 확인할 수 있습니다.

-----

## 라이선스 및 고지 사항

**데이터 권리**: 본 프로젝트에서 분석된 메타데이터 및 기사 콘텐츠의 소유권은 \*\*BIGKINDS(한국언론진흥재단)\*\*에 있습니다.
**사용 범위**: 이 프로젝트는 **교육 및 연구 목적**으로만 사용됩니다. 원 저작권자의 허가 없이 크롤링된 데이터를 상업적으로 사용하는 것은 엄격히 금지됩니다.
**폰트**: 해당 프로젝트는 [Pretendard](https://github.com/orioncactus/pretendard) 폰트를 사용합니다, 라이센스는 [SIL Open Font License 1.1](/fonts/LICENSE.txt)에 명시되어있습니다.

MIT License © 2025 Byeonghyeon Na

