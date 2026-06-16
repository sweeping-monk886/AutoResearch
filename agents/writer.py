from typing import Dict, Any, List, Optional
import json


WRITER_SYSTEM_PROMPT = """你是一个专业的学术报告撰写者。请根据以下信息撰写一份完整的研究报告。

研究主题: {topic}
报告大纲: {outline}
收集的资料: {materials}
分析结果: {analysis}

要求：
1. 语言专业、客观、流畅
2. 结构清晰，每个章节有明确标题
3. 引用具体数据和来源
4. 总结核心观点和未来方向
5. 包含参考文献列表
"""


class WriterAgent:
    """写作智能体：将检索和分析结果整合成结构化报告。"""

    def __init__(self, llm_call=None):
        self.llm_call = llm_call

    def write(self, topic: str, outline: List[str], materials: Dict[str, Any], analyses: List[str]) -> str:
        """生成完整研究报告。"""
        if self.llm_call:
            return self._llm_write(topic, outline, materials, analyses)
        return self._template_write(topic, outline, materials, analyses)

    def _template_write(self, topic: str, outline: List[str], materials: Dict[str, Any], analyses: List[str]) -> str:
        report_parts = []
        report_parts.append(self._write_header(topic))
        report_parts.append(self._write_abstract(topic, materials, analyses))

        section_contents = {
            "摘要": None,
            "研究背景": self._write_background(topic, materials),
            "技术现状": self._write_tech_status(topic, materials),
            "关键发现": self._write_findings(analyses),
            "对比分析": self._write_comparison(analyses),
            "未来趋势": self._write_future(topic, analyses),
            "结论": self._write_conclusion(topic, analyses),
            "参考文献": self._write_references(materials),
        }

        for section in outline:
            if section in section_contents and section_contents[section]:
                report_parts.append(section_contents[section])

        return "\n\n".join(report_parts)

    def _llm_write(self, topic, outline, materials, analyses) -> str:
        mat_text = json.dumps(materials, ensure_ascii=False, default=str)[:4000]
        prompt = WRITER_SYSTEM_PROMPT.format(
            topic=topic, outline="\n".join(outline), materials=mat_text, analysis="\n\n".join(analyses[:3])
        )
        return self.llm_call(prompt)

    def _write_header(self, topic: str) -> str:
        return f"# {topic} — 研究报告\n\n> 本报告由 AutoResearch 多智能体系统自动生成"

    def _write_abstract(self, topic, materials, analyses) -> str:
        web_count = len(materials.get("web_results", []))
        arxiv_count = len(materials.get("arxiv_results", []))
        return f"""## 摘要

本报告对 **{topic}** 进行了系统性研究，综合网络检索 {web_count} 条结果、学术论文 {arxiv_count} 篇，通过多智能体协作完成了信息检索、深度分析和报告生成。报告涵盖了该领域的研究背景、技术现状、关键发现、对比分析及未来趋势。"""

    def _write_background(self, topic, materials) -> str:
        parts = [f"## 研究背景\n\n### {topic} 的基本概念\n"]
        rag = materials.get("rag_results", [])
        if rag and rag[0].get("context") and rag[0]["context"] != "[知识库中未找到相关信息]":
            parts.append(rag[0]["context"][:1000])
        else:
            parts.append(f"**{topic}** 是当前研究的热点领域。以下从多个维度梳理其研究背景。\n")
            web = materials.get("web_results", [])
            if web:
                parts.append("\n### 相关背景资料\n")
                for r in web[:3]:
                    parts.append(f"- **{r.get('title', 'N/A')}**: {r.get('snippet', '')[:150]}\n")
        return "\n".join(parts)

    def _write_tech_status(self, topic, materials) -> str:
        parts = [f"## 技术现状\n"]
        arxiv = materials.get("arxiv_results", [])
        if arxiv:
            parts.append("### 最新学术研究\n")
            for p in arxiv[:5]:
                parts.append(f"**{p.get('title', 'N/A')}** ({p.get('published', '')[:4]})")
                parts.append(f"- 作者: {', '.join(p.get('authors', [])[:3])}")
                parts.append(f"- 摘要: {p.get('summary', '')[:300]}\n")
        fetched = materials.get("fetched_pages", [])
        if fetched:
            parts.append("### 行业动态\n")
            for page in fetched[:2]:
                parts.append(f"**{page.get('title', 'N/A')}**\n{page.get('content', '')[:500]}\n")
        if len(parts) == 1:
            parts.append("（暂未检索到足够的技术资料）\n")
        return "\n".join(parts)

    def _write_findings(self, analyses) -> str:
        parts = ["## 关键发现\n"]
        for i, a in enumerate(analyses, 1):
            parts.append(f"### 发现 {i}\n{a[:800]}\n")
        return "\n".join(parts)

    def _write_comparison(self, analyses) -> str:
        parts = ["## 对比分析\n"]
        if len(analyses) >= 2:
            parts.append("基于多维度分析，以下为对比总结：\n")
            for a in analyses[:2]:
                parts.append(f"{a[:400]}\n")
        else:
            parts.append("单维度分析结果如上所示。\n")
        return "\n".join(parts)

    def _write_future(self, topic, analyses) -> str:
        parts = [f"## 未来趋势\n\n基于当前研究，{topic} 的未来发展方向可能包括：\n"]
        parts.append("1. **技术融合**: 多技术交叉融合将持续推动创新\n")
        parts.append("2. **应用拓展**: 从特定领域向更广泛应用场景延伸\n")
        parts.append("3. **效率优化**: 追求更高的性能和更低的成本\n")
        parts.append("4. **标准化**: 行业标准和最佳实践将逐步建立\n")
        return "\n".join(parts)

    def _write_conclusion(self, topic, analyses) -> str:
        return f"""## 结论

本报告对 **{topic}** 进行了全面研究，主要结论如下：

1. 该领域目前正处于快速发展阶段，研究热度持续上升
2. 多项关键技术已取得重要突破，为实际应用奠定了基础
3. 仍存在一些挑战需要解决，包括技术成熟度、标准化等问题
4. 未来发展前景广阔，值得持续关注和投入

本报告由 AutoResearch 多智能体系统自动生成，结合了网络检索、学术论文分析和深度推理。"""

    def _write_references(self, materials) -> str:
        parts = ["## 参考文献\n"]
        arxiv = materials.get("arxiv_results", [])
        for i, p in enumerate(arxiv, 1):
            parts.append(f"[{i}] {p.get('title', 'N/A')}. {', '.join(p.get('authors', [])[:3])}. {p.get('published', '')[:4]}")
            parts.append(f"    {p.get('link', '')}\n")
        web = materials.get("web_results", [])
        for i, r in enumerate(web[:5], len(arxiv) + 1):
            parts.append(f"[{i}] {r.get('title', 'N/A')}. {r.get('url', '')}\n")
        return "\n".join(parts)
