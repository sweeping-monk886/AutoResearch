from typing import Dict, Any, List, Optional
from tools.search_tool import WebSearchTool, ArxivSearchTool
from config.settings import Settings


class RetrieverAgent:
    """检索智能体：负责从网络和知识库中检索信息。"""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.web_search = WebSearchTool(max_results=self.settings.search_max_results)
        self.arxiv_search = ArxivSearchTool()
        self.rag = None
        self.results_cache: Dict[str, Any] = {}

    def _get_rag(self):
        if self.rag is None:
            try:
                from tools.rag_tool import RAGRetrieverTool
                self.rag = RAGRetrieverTool(self.settings)
            except Exception:
                self.rag = False
        return self.rag if self.rag else None

    def retrieve(self, task_id: str, description: str, keywords: List[str]) -> Dict[str, Any]:
        query = description
        all_results = {
            "task_id": task_id,
            "query": query,
            "web_results": [],
            "arxiv_results": [],
            "rag_results": [],
            "combined_text": "",
        }

        rag = self._get_rag()
        if rag:
            try:
                rag_ctx = rag.build_context(query, top_k=3)
                all_results["rag_results"] = [{"context": rag_ctx}]
            except Exception:
                pass

        web = self.web_search.run(query)
        all_results["web_results"] = web.get("results", [])

        arxiv = self.arxiv_search.run(query, max_results=3)
        all_results["arxiv_results"] = arxiv.get("papers", [])

        fetched = []
        for r in all_results["web_results"][:3]:
            url = r.get("url", "")
            if url:
                content = self.web_search.fetch_page(url)
                if content and not content.startswith("[页面获取失败"):
                    fetched.append({"url": url, "title": r.get("title", ""), "content": content})
        all_results["fetched_pages"] = fetched

        parts = []
        rag_ctx = all_results.get("rag_results", [{}])
        if rag_ctx and rag_ctx[0].get("context", "") not in ["", "[知识库中未找到相关信息]"]:
            parts.append(f"## 知识库检索\n{rag_ctx[0]['context']}")
        if all_results["web_results"]:
            web_text = "\n".join(f"- {r['title']}: {r['snippet']}" for r in all_results["web_results"][:5])
            parts.append(f"## 网络搜索结果\n{web_text}")
        if all_results["arxiv_results"]:
            arxiv_text = "\n".join(
                f"- {p['title']} ({p['published'][:4]}): {p['summary'][:200]}"
                for p in all_results["arxiv_results"][:3]
            )
            parts.append(f"## 学术论文\n{arxiv_text}")
        for page in fetched[:2]:
            parts.append(f"## {page['title']}\n{page['content'][:1000]}")

        all_results["combined_text"] = "\n\n---\n\n".join(parts) if parts else "[未找到相关信息]"
        self.results_cache[task_id] = all_results
        return all_results

    def index_to_rag(self, documents: List[Dict[str, str]]) -> int:
        rag = self._get_rag()
        if rag:
            return rag.index_documents(documents)
        return 0
