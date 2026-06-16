import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import List, Dict, Any


class WebSearchTool:
    """通过DuckDuckGo进行网络搜索，获取最新信息。"""

    def __init__(self, max_results: int = 8):
        self.max_results = max_results

    def run(self, query: str) -> Dict[str, Any]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
            return {"query": query, "results": formatted, "count": len(formatted)}
        except Exception as e:
            return {"query": query, "results": [], "error": str(e)}

    def fetch_page(self, url: str, max_chars: int = 3000) -> str:
        try:
            resp = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            resp.encoding = resp.apparent_encoding
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            return text[:max_chars]
        except Exception as e:
            return f"[页面获取失败: {e}]"


class ArxivSearchTool:
    """从ArXiv检索学术论文。"""

    BASE_URL = "http://export.arxiv.org/api/query"

    def run(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        try:
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
            }
            resp = requests.get(self.BASE_URL, params=params, timeout=15)
            soup = BeautifulSoup(resp.text, "xml")
            entries = soup.find_all("entry")
            papers = []
            for entry in entries:
                papers.append({
                    "title": entry.title.get_text(strip=True),
                    "authors": [a.get_text(strip=True) for a in entry.find_all("author")],
                    "summary": entry.summary.get_text(strip=True),
                    "published": entry.published.get_text(strip=True),
                    "link": entry.id.get_text(strip=True),
                    "categories": [c["term"] for c in entry.find_all("category")],
                })
            return {"query": query, "papers": papers, "count": len(papers)}
        except Exception as e:
            return {"query": query, "papers": [], "error": str(e)}
