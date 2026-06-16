from typing import Dict, Any, Optional
from tools.analysis_tool import TextAnalysisTool, CodeExecutorTool


ANALYST_SYSTEM_PROMPT = """你是一个专业的内容分析师。请对以下信息进行深度分析：

分析任务: {task}
参考资料: {context}

请提供：
1. 核心要点总结（3-5个关键发现）
2. 技术/方法分析
3. 优势与局限性
4. 数据或案例支撑
5. 与其他方案的对比

输出格式：
## 分析报告
### 核心发现
...
### 详细分析
...
### 总结
...
"""


class AnalystAgent:
    """分析智能体：对检索信息进行深度处理和分析。"""

    def __init__(self, llm_call=None):
        self.llm_call = llm_call
        self.text_analyzer = TextAnalysisTool()
        self.code_executor = CodeExecutorTool()
        self.analysis_cache: Dict[str, str] = {}

    def analyze(self, task_id: str, description: str, context: str) -> Dict[str, Any]:
        """对给定上下文进行深度分析。"""
        # 文本统计分析
        stats = self.text_analyzer.run(context)

        # LLM深度分析
        if self.llm_call:
            analysis = self._llm_analyze(description, context)
        else:
            analysis = self._template_analyze(description, context)

        result = {
            "task_id": task_id,
            "description": description,
            "text_stats": stats,
            "analysis": analysis,
        }
        self.analysis_cache[task_id] = analysis
        return result

    def execute_code(self, code: str) -> Dict[str, Any]:
        return self.code_executor.run(code)

    def _template_analyze(self, description: str, context: str) -> str:
        key_points = []
        lines = context.split("\n")
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith("[") and not line.startswith("---"):
                if any(kw in line.lower() for kw in ["发现", "结果", "证明", "表明", "分析", "conclusion", "result"]):
                    key_points.append(line[:200])

        if not key_points:
            for line in lines:
                if line.strip() and len(line.strip()) > 20:
                    key_points.append(line.strip()[:200])
                if len(key_points) >= 5:
                    break

        analysis = f"### 核心发现\n\n"
        for i, point in enumerate(key_points[:5], 1):
            analysis += f"{i}. {point}\n\n"

        analysis += f"\n### 详细分析\n\n"
        analysis += f"针对 **{description}** 的分析：\n\n"

        if stats := self.text_analyzer.run(context):
            analysis += f"- 参考资料共 {stats['word_count']} 词\n"
            analysis += f"- 包含 {stats['cn_char_count']} 个中文字符\n"
            if stats["top_keywords"]:
                kw_str = ", ".join(k["word"] for k in stats["top_keywords"][:5])
                analysis += f"- 关键词: {kw_str}\n"

        analysis += f"\n### 总结\n\n"
        analysis += f"基于对检索资料的分析，{description}的要点已归纳如上。"
        return analysis

    def _llm_analyze(self, description: str, context: str) -> str:
        prompt = ANALYST_SYSTEM_PROMPT.format(task=description, context=context[:4000])
        return self.llm_call(prompt)
