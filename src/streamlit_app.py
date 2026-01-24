from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from insight_agent import generate_insight


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TS_PATH = BASE_DIR / "preprocessed" / "top10_monthly_timeseries.csv"


def load_timeseries(path: Path = DEFAULT_TS_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df[["year", "month"]].assign(day=1))
    return df


def compute_surge_keywords(
    df: pd.DataFrame,
    start_date: date,
    end_date: date,
    top_n: int = 5,
) -> List[dict]:
    # 기간 필터링 시 복사본 생성
    mask = (df["date"] >= pd.Timestamp(start_date)) & (df["date"] <= pd.Timestamp(end_date))
    period = df[mask].copy()
    if period.empty:
        return []

    period = period.sort_values("date")
    grouped = period.groupby("keyword")
    
    # 단순히 first/last를 취하기보다 시작점과 끝점의 존재 여부 확인
    summary = grouped.agg(
        first_val=('count', 'first'),
        last_val=('count', 'last')
    ).reset_index()

    summary["change"] = summary["last_val"] - summary["first_val"]
    
    # 0으로 나누기 방지 및 급등 지수 계산 개선
    # 시작값이 0인 경우 0.5 정도로 보정하여 변화율 계산 (폭발적 증가 반영)
    summary["pct_change"] = summary["change"] / (summary["first_val"].replace(0, 0.5))
    
    summary = summary.sort_values("pct_change", ascending=False).head(top_n)

    return summary.rename(columns={
        "first_val": "first", "last_val": "last"
    }).to_dict(orient="records")


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="Trend Insight", layout="wide")
    st.title("이슈 급등 감지 + 요약")

    if not DEFAULT_TS_PATH.exists():
        st.error(f"데이터 파일을 찾을 수 없습니다: {DEFAULT_TS_PATH}")
        return

    df = load_timeseries()
    keywords = (
        df.groupby("keyword")["count"]
        .sum()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    default_keywords = keywords[:5]

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    if "selected_range" not in st.session_state:
        st.session_state.selected_range = (min_date, max_date)
    if "selected_keywords" not in st.session_state:
        st.session_state.selected_keywords = default_keywords
    if "top_n" not in st.session_state:
        st.session_state.top_n = 5

    with st.form("analysis_form"):
        st.subheader("분석 조건 입력")
        selected_keywords = st.multiselect(
            "키워드 선택",
            options=keywords,
            default=st.session_state.selected_keywords,
        )
        picked = st.date_input(
            "기간 선택",
            value=st.session_state.selected_range,
            min_value=min_date,
            max_value=max_date,
        )
        top_n = st.slider("급등 키워드 개수", min_value=3, max_value=10, value=st.session_state.top_n)
        submitted = st.form_submit_button("적용")

    if submitted:
        if isinstance(picked, (list, tuple)) and len(picked) == 2:
            st.session_state.selected_range = picked
        st.session_state.selected_keywords = selected_keywords
        st.session_state.top_n = top_n

    selected_keywords = st.session_state.selected_keywords
    top_n = st.session_state.top_n
    start_date, end_date = st.session_state.selected_range

    if selected_keywords:
        chart_df = df[df["keyword"].isin(selected_keywords)].copy()
    else:
        chart_df = df.head(0).copy()
    fig = px.line(
        chart_df,
        x="date",
        y="count",
        color="keyword",
        markers=True,
        title="월별 키워드 시계열 (선택 구간 드래그)",
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, width="stretch")

    surge_rows = compute_surge_keywords(chart_df, start_date, end_date, top_n=top_n)
    st.subheader("급등 키워드 요약")
    if not selected_keywords:
        st.warning("키워드를 최소 1개 이상 선택하세요.")
    elif surge_rows:
        st.dataframe(pd.DataFrame(surge_rows), width="stretch")
    else:
        st.warning("선택 기간에 급등 키워드가 없습니다.")

    st.subheader("설명 요청")
    default_prompt = "해당 기간에 대해서 설명해줘."
    user_prompt = st.text_area("프롬프트", value=default_prompt, height=100)

    if st.button("웹 검색 + 요약"):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY가 설정되어 있지 않습니다. .env 또는 환경변수에 추가하세요.")
            return

        with st.spinner("검색 및 요약 생성 중..."):
            result = generate_insight(
                start_date=start_date,
                end_date=end_date,
                surge_rows=surge_rows,
                user_prompt=user_prompt,
            )

        st.subheader("요약 결과")
        st.markdown(result["content"])

        if result["sources"]:
            st.subheader("참고 자료")
            for i, src in enumerate(result["sources"], start=1):
                st.markdown(f"[{i}] {src.title} - {src.url}")


if __name__ == "__main__":
    main()
