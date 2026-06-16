import re
import json
import traceback
from typing import Dict, Any
from collections import Counter


class TextAnalysisTool:
    """文本分析工具：统计关键词、摘要长度等。"""

    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "and", "but", "or",
        "not", "no", "nor", "so", "yet", "both", "either", "neither", "each",
        "every", "all", "any", "few", "more", "most", "other", "some", "such",
        "this", "that", "these", "those", "it", "its", "they", "them", "their",
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
        "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    }

    def run(self, text: str) -> Dict[str, Any]:
        words = text.split()
        meaningful = [
            w.lower().strip(".,!?;:\"'()[]{}")
            for w in words
            if len(w) > 2 and w.lower() not in self.STOP_WORDS and w.isalpha()
        ]
        cn_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return {
            "word_count": len(words),
            "char_count": len(text),
            "cn_char_count": len(cn_chars),
            "sentence_count": max(1, len(re.split(r'[.!?。！？]', text)) - 1),
            "reading_time_min": round(len(words) / 200, 2),
            "top_keywords": [
                {"word": w, "count": c} for w, c in Counter(meaningful).most_common(10)
            ],
        }


class CodeExecutorTool:
    """安全的Python代码执行沙箱。"""

    SAFE_GLOBALS = {
        "__builtins__": {},
        "range": range, "len": len, "min": min, "max": max,
        "sum": sum, "sorted": sorted, "enumerate": enumerate,
        "zip": zip, "map": map, "filter": filter, "list": list,
        "dict": dict, "set": set, "tuple": tuple, "str": str,
        "int": int, "float": float, "bool": bool, "abs": abs,
        "round": round, "pow": pow, "divmod": divmod,
        "isinstance": isinstance, "type": type, "print": print,
        "json": json, "re": re, "Counter": Counter,
    }

    def run(self, code: str) -> Dict[str, Any]:
        local_ns = {}
        try:
            exec(code, self.SAFE_GLOBALS, local_ns)
            output = local_ns.get("_result", None)
            return {"success": True, "result": str(output), "variables": {
                k: str(v) for k, v in local_ns.items() if not k.startswith("_")
            }}
        except Exception as e:
            return {"success": False, "error": f"{type(e).__name__}: {e}",
                    "traceback": traceback.format_exc()}
