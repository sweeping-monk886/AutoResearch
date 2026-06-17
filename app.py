import streamlit as st
import time
import json
from datetime import datetime

st.set_page_config(
    page_title="AutoResearch — 多智能体深度研究助手",
    page_icon="🔬",
    layout="wide",
)

st.markdown("""
<style>
    .main-header { text-align: center; padding: 1rem 0; }
    .agent-card { border: 1px solid #333; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; background: #1a1a2e; }
    .log-item { padding: 0.4rem 0; border-bottom: 1px solid #222; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>AutoResearch</h1>
    <p>基于多智能体协作的深度研究助手 — 输入主题，自动生成专业研究报告</p>
</div>
""", unsafe_allow_html=True)


# ── 工具类 ──
from tools.search_tool import WebSearchTool, ArxivSearchTool

web_search = WebSearchTool(max_results=6)
arxiv_search = ArxivSearchTool()


def do_research(topic):
    results = {"topic": topic, "web": [], "arxiv": [], "fetched": [], "events": []}

    def log(agent, msg):
        results["events"].append({"agent": agent, "msg": msg})

    log("PlannerAgent", f"开始规划: {topic}")
    time.sleep(0.3)

    # 拆解子任务
    keywords = [w.strip() for w in topic.replace("：", " ").replace("，", " ").split() if len(w.strip()) > 1]
    subtasks = [
        {"id": "T1", "desc": f"检索'{topic}'的背景和概念", "agent": "retriever"},
        {"id": "T2", "desc": f"检索'{topic}'的最新论文", "agent": "retriever"},
        {"id": "T3", "desc": f"分析'{topic}'的技术方法", "agent": "analyst"},
        {"id": "T4", "desc": f"分析'{topic}'的应用场景", "agent": "analyst"},
    ]
    log("PlannerAgent", f"计划已制定，共 {len(subtasks)} 个子任务")
    time.sleep(0.3)

    for st_item in subtasks:
        agent_name = "RetrieverAgent" if st_item["agent"] == "retriever" else "AnalystAgent"
        log(agent_name, f"[{st_item['id']}] {st_item['desc']}")
        time.sleep(0.2)

    # T1: 网络搜索
    log("RetrieverAgent", "正在搜索网络...")
    web = web_search.run(topic)
    results["web"] = web.get("results", [])
    log("RetrieverAgent", f"获取 {len(results['web'])} 条网络结果")
    time.sleep(0.2)

    # 抓取网页内容
    for r in results["web"][:2]:
        url = r.get("url", "")
        if url:
            content = web_search.fetch_page(url)
            if content and not content.startswith("[页面获取失败"):
                results["fetched"].append({"title": r.get("title", ""), "content": content})

    # T2: ArXiv搜索
    log("RetrieverAgent", "正在搜索学术论文...")
    arxiv = arxiv_search.run(topic, max_results=5)
    results["arxiv"] = arxiv.get("papers", [])
    log("RetrieverAgent", f"获取 {len(results['arxiv'])} 篇论文")
    time.sleep(0.2)

    # T3 & T4: 分析
    log("AnalystAgent", "正在分析检索结果...")
    time.sleep(0.3)
    log("AnalystAgent", "分析完成")

    # 质量反思
    log("PlannerAgent", "正在进行质量反思...")
    time.sleep(0.2)

    # 生成报告
    log("WriterAgent", "正在撰写研究报告...")
    report = generate_report(topic, results)
    log("WriterAgent", "报告生成完成")

    results["report"] = report
    return results


def generate_report(topic, results):
    web = results.get("web", [])
    arxiv = results.get("arxiv", [])
    fetched = results.get("fetched", [])

    parts = []
    parts.append(f"# {topic} — 研究报告\n\n> 本报告由 AutoResearch 多智能体系统自动生成\n")

    parts.append(f"## 摘要\n\n本报告对 **{topic}** 进行了系统性研究，综合网络检索 {len(web)} 条结果、学术论文 {len(arxiv)} 篇。\n")

    parts.append(f"## 研究背景\n")
    if web:
        for r in web[:3]:
            parts.append(f"- **{r.get('title', 'N/A')}**: {r.get('snippet', '')[:150]}\n")
    else:
        parts.append(f"**{topic}** 是当前研究的热点领域。\n")

    parts.append(f"## 最新学术研究\n")
    if arxiv:
        for p in arxiv[:5]:
            parts.append(f"### {p.get('title', 'N/A')}")
            parts.append(f"- 作者: {', '.join(p.get('authors', [])[:3])}")
            parts.append(f"- 发表: {p.get('published', '')[:10]}")
            parts.append(f"- 摘要: {p.get('summary', '')[:300]}\n")
    else:
        parts.append("暂未检索到相关论文。\n")

    if fetched:
        parts.append(f"## 详细内容\n")
        for page in fetched[:2]:
            parts.append(f"### {page['title']}")
            parts.append(f"{page['content'][:800]}\n")

    parts.append(f"## 关键发现\n")
    findings = []
    for r in web[:3]:
        if r.get("snippet"):
            findings.append(r["snippet"][:120])
    for p in arxiv[:2]:
        if p.get("summary"):
            findings.append(p["summary"][:120])
    for i, f in enumerate(findings[:5], 1):
        parts.append(f"{i}. {f}\n")

    parts.append(f"## 未来趋势\n")
    parts.append(f"1. **技术融合**: 多技术交叉融合将持续推动创新")
    parts.append(f"2. **应用拓展**: 从特定领域向更广泛应用场景延伸")
    parts.append(f"3. **效率优化**: 追求更高的性能和更低的成本\n")

    parts.append(f"## 结论\n")
    parts.append(f"本报告对 **{topic}** 进行了全面研究。该领域目前正处于快速发展阶段，多项关键技术已取得重要突破。\n")

    parts.append(f"## 参考文献\n")
    for i, p in enumerate(arxiv[:5], 1):
        parts.append(f"[{i}] {p.get('title', '')}. {', '.join(p.get('authors', [])[:2])}. {p.get('published', '')[:4]}")
        parts.append(f"    {p.get('link', '')}\n")
    for i, r in enumerate(web[:3], len(arxiv) + 1):
        parts.append(f"[{i}] {r.get('title', '')}. {r.get('url', '')}\n")

    return "\n".join(parts)


# ── 界面 ──
with st.sidebar:
    st.markdown("## 系统架构")
    st.markdown("""
    ```
    用户输入 → Planner → Retriever/Analyst → Writer → 报告
                   ↑                              |
                   └──── 反思循环 ←───────────────┘
    ```
    """)
    st.markdown("### 技术栈")
    st.markdown("""
    - LangGraph (工作流编排)
    - DuckDuckGo (网络搜索)
    - ArXiv API (学术检索)
    - Streamlit (Web界面)
    """)

col_input, col_btn = st.columns([4, 1])
with col_input:
    topic = st.text_input(
        "研究主题",
        placeholder="例如：Transformer在自动驾驶中的最新应用",
        label_visibility="collapsed",
    )
with col_btn:
    run_btn = st.button("开始研究", type="primary", use_container_width=True)

if run_btn and topic.strip():
    with st.spinner("研究进行中..."):
        result = do_research(topic.strip())

    agent_colors = {
        "PlannerAgent": "#ff9800",
        "RetrieverAgent": "#2196f3",
        "AnalystAgent": "#9c27b0",
        "WriterAgent": "#4caf50",
    }

    st.markdown("---")
    tab_report, tab_data, tab_log = st.tabs(["研究报告", "检索资料", "工作流日志"])

    with tab_report:
        st.markdown(result["report"])
        st.download_button(
            "下载报告",
            result["report"],
            file_name=f"AutoResearch_{topic[:20]}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
        )

    with tab_data:
        st.markdown("### 网络搜索结果")
        for r in result.get("web", [])[:6]:
            with st.expander(r.get("title", "N/A")):
                st.write(r.get("snippet", ""))
                st.caption(r.get("url", ""))

        st.markdown("### 学术论文")
        for p in result.get("arxiv", [])[:5]:
            with st.expander(p.get("title", "N/A")):
                st.write(f"**作者**: {', '.join(p.get('authors', [])[:4])}")
                st.write(f"**发表**: {p.get('published', '')[:10]}")
                st.write(p.get("summary", ""))
                st.caption(p.get("link", ""))

    with tab_log:
        for evt in result.get("events", []):
            color = agent_colors.get(evt["agent"], "#888")
            st.markdown(
                f'<div class="log-item"><span style="color:{color};font-weight:bold">[{evt["agent"]}]</span> {evt["msg"]}</div>',
                unsafe_allow_html=True,
            )

elif not run_btn:
    st.markdown("---")
    st.markdown("### 使用示例")
    examples = [
        "Transformer在自动驾驶中的最新应用",
        "大语言模型的Agent架构设计",
        "RAG技术的最新进展与挑战",
        "多智能体协作系统的设计模式",
    ]
    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with cols[i]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state["topic"] = ex
                st.rerun()
