from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Optional

from ddgs import DDGS
from openai import OpenAI


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    keyword: str


def _build_queries(
    keywords: Iterable[str],
    start_date: date,
    end_date: date,
) -> List[str]:
    start_label = start_date.strftime("%Y-%m")
    end_label = end_date.strftime("%Y-%m")
    queries = []
    for kw in keywords:
        queries.append(f"{kw} {start_label} {end_label} 한국 이슈")
    return queries


def search_web(
    keywords: Iterable[str],
    start_date: date,
    end_date: date,
    max_results_per_keyword: int = 4,
) -> List[SearchResult]:
    keywords_list = list(keywords)
    if not keywords_list:
        return []

    queries = _build_queries(keywords_list, start_date, end_date)
    results: List[SearchResult] = []
    seen = set()

    with DDGS() as ddgs:
        for idx, query in enumerate(queries):
            kw = keywords_list[idx]
            for item in ddgs.text(query, max_results=max_results_per_keyword):
                url = item.get("href") or item.get("url")
                if not url or url in seen:
                    continue
                seen.add(url)
                results.append(
                    SearchResult(
                        title=item.get("title", "").strip(),
                        url=url,
                        snippet=item.get("body", "").strip(),
                        keyword=kw,
                    )
                )
    return results


def _format_sources(results: List[SearchResult]) -> str:
    lines = []
    for i, r in enumerate(results, start=1):
        title = r.title or r.url
        snippet = r.snippet.replace("\n", " ").strip()
        lines.append(f"[{i}] {title} - {snippet} ({r.url})")
    return "\n".join(lines)


def _build_prompt(
    start_date: date,
    end_date: date,
    surge_rows: List[dict],
    user_prompt: str,
    sources_block: str,
) -> str:
    period = f"{start_date:%Y-%m} ~ {end_date:%Y-%m}"
    surge_lines = []
    for row in surge_rows:
        surge_lines.append(
            f"- {row['keyword']}: first={row['first']}, last={row['last']}, change={row['change']}, pct_change={row['pct_change']:.2f}"
        )
    surge_text = "\n".join(surge_lines) if surge_lines else "- (no surge keywords)"

    return (
        "You are a research assistant. Answer in Korean.\n"
        "Use the sources to ground your explanation. Cite sources like [1], [2].\n\n"
        f"기간: {period}\n"
        "급등 키워드(요약 데이터):\n"
        f"{surge_text}\n\n"
        f"사용자 요청: {user_prompt}\n\n"
        "웹 검색 결과:\n"
        f"{sources_block}\n\n"
        "출력 형식:\n"
        "1) 요약(2~3문장)\n"
        "2) 키워드별 근거(키워드 -> 사건/이슈 설명)\n"
        "3) 인사이트(1~2문장)\n"
    )


def summarize_with_openai(prompt: str, model: Optional[str] = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a concise analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def generate_insight(
    start_date: date,
    end_date: date,
    surge_rows: List[dict],
    user_prompt: str,
    max_results_per_keyword: int = 4,
) -> dict:
    keywords = [row["keyword"] for row in surge_rows]
    if not keywords:
        keywords = []

    results = search_web(
        keywords=keywords,
        start_date=start_date,
        end_date=end_date,
        max_results_per_keyword=max_results_per_keyword,
    )

    sources_block = _format_sources(results)
    prompt = _build_prompt(start_date, end_date, surge_rows, user_prompt, sources_block)

    content = summarize_with_openai(prompt)
    return {
        "content": content,
        "sources": results,
        "prompt": prompt,
    }
