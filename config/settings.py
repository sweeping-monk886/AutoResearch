import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    # LLM Config
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))

    # Embedding Config
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    embedding_dim: int = 384

    # Vector Store Config
    chroma_persist_dir: str = field(default_factory=lambda: os.getenv("CHROMA_DIR", "./chroma_db"))
    chroma_collection: str = "research_papers"

    # Search Config
    search_max_results: int = 8

    # Agent Config
    max_iterations: int = 10
    reflection_threshold: int = 3

    # Report Config
    report_sections: list = field(default_factory=lambda: [
        "摘要", "研究背景", "技术现状", "关键发现", "对比分析", "未来趋势", "结论", "参考文献"
    ])
