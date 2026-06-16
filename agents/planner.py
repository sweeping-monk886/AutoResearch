from typing import Dict, Any, List, TypedDict


class ResearchPlan(TypedDict):
    topic: str
    subtasks: List[Dict[str, str]]
    keywords: List[str]
    search_queries: List[str]
    report_outline: List[str]


PLANNER_SYSTEM_PROMPT = """你是一个专业的研究规划专家。你的任务是：
1. 分析用户的研究主题
2. 将其分解为具体的、可执行的子任务
3. 为每个子任务生成精确的搜索关键词
4. 设计报告大纲

输出JSON格式：
{
    "topic": "研究主题",
    "subtasks": [
        {"id": "T1", "description": "子任务描述", "agent": "retriever"},
        {"id": "T2", "description": "子任务描述", "agent": "analyst"}
    ],
    "keywords": ["关键词1", "关键词2", ...],
    "search_queries": ["搜索查询1", "搜索查询2", ...],
    "report_outline": ["章节1", "章节2", ...]
}

注意：
- 子任务应该覆盖：背景调研、技术现状、关键发现、对比分析、趋势预测
- 搜索查询应该具体、精确，避免过于宽泛
- agent字段只能是 "retriever" 或 "analyst"
"""

REFLECTION_PROMPT = """你是一个研究质量审查专家。请评估当前研究进展：

研究主题: {topic}
已完成的子任务: {completed_tasks}
已有信息: {collected_info}

请回答以下问题（JSON格式）：
{{
    "is_sufficient": true/false,
    "gaps": ["缺失的信息1", "缺失的信息2"],
    "suggestions": ["建议的补充检索1", "建议的补充检索2"],
    "quality_score": 0-100
}}

is_sufficient为true表示信息足够生成报告，false表示需要补充。"""


class PlannerAgent:
    """规划智能体：负责任务分解、计划制定和全局协调。"""

    def __init__(self, llm_call=None):
        self.llm_call = llm_call
        self.plan = None
        self.completed_tasks = []
        self.reflection_count = 0

    def create_plan(self, topic: str) -> ResearchPlan:
        if self.llm_call:
            return self._llm_plan(topic)
        return self._template_plan(topic)

    def reflect(self, topic: str, completed: List[str], info: str) -> Dict[str, Any]:
        if self.llm_call:
            return self._llm_reflect(topic, completed, info)
        return self._template_reflect(topic, completed, info)

    def _template_plan(self, topic: str) -> ResearchPlan:
        keywords = [w.strip() for w in topic.replace("：", " ").replace("，", " ").split() if len(w.strip()) > 1]
        subtasks = [
            {"id": "T1", "description": f"检索'{topic}'的研究背景和基本概念", "agent": "retriever"},
            {"id": "T2", "description": f"检索'{topic}'的最新技术进展和关键论文", "agent": "retriever"},
            {"id": "T3", "description": f"分析'{topic}'的核心技术方法", "agent": "analyst"},
            {"id": "T4", "description": f"分析'{topic}'的主要应用场景和案例", "agent": "analyst"},
            {"id": "T5", "description": f"分析'{topic}'的优势、局限性和未来趋势", "agent": "analyst"},
            {"id": "T6", "description": f"综合整理'{topic}'的对比分析和总结", "agent": "analyst"},
        ]
        outline = ["摘要", "研究背景", "技术现状", "关键发现", "对比分析", "未来趋势", "结论", "参考文献"]
        return ResearchPlan(
            topic=topic,
            subtasks=subtasks,
            keywords=keywords,
            search_queries=[topic, f"{topic} latest research", f"{topic} applications"],
            report_outline=outline,
        )

    def _llm_plan(self, topic: str) -> ResearchPlan:
        prompt = f"{PLANNER_SYSTEM_PROMPT}\n\n请为以下研究主题制定计划：\n{topic}"
        response = self.llm_call(prompt)
        try:
            import json
            data = json.loads(response)
            return ResearchPlan(**data)
        except Exception:
            return self._template_plan(topic)

    def _template_reflect(self, topic, completed, info) -> Dict[str, Any]:
        score = min(100, len(completed) * 20)
        return {
            "is_sufficient": len(completed) >= 4,
            "gaps": [] if len(completed) >= 4 else ["需要更多深度分析"],
            "suggestions": [],
            "quality_score": score,
        }

    def _llm_reflect(self, topic, completed, info) -> Dict[str, Any]:
        prompt = REFLECTION_PROMPT.format(topic=topic, completed_tasks=completed, collected_info=info[:2000])
        response = self.llm_call(prompt)
        try:
            import json
            return json.loads(response)
        except Exception:
            return self._template_reflect(topic, completed, info)
