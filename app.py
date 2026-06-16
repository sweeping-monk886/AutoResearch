import streamlit as st
import time
import json
from datetime import datetime


@st.cache_resource
def load_workflow():
    from config.settings import Settings
    from agents.workflow import ResearchWorkflow
    settings = Settings()
    return ResearchWorkflow(settings)


st.set_page_config(
    page_title="AutoResearch — 多智能体深度研究助手",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main-header { text-align: center; padding: 1rem 0; }
    .main-header h1 { font-size: 2.2rem; margin-bottom: 0.3rem; }
    .main-header p { color: #888; font-size: 1rem; }
    .agent-card {
        border: 1px solid #333; border-radius: 10px; padding: 1rem;
        margin: 0.5rem 0; background: #1a1a2e;
    }
    .agent-card h4 { margin: 0 0 0.5rem 0; color: #00d4ff; }
    .status-badge {
        display: inline-block; padding: 2px 10px; border-radius: 12px;
        font-size: 0.75rem; font-weight: bold;
    }
    .status-running { background: #ff9800; color: #000; }
    .status-done { background: #4caf50; color: #fff; }
    .status-pending { background: #555; color: #fff; }
    .log-item { padding: 0.4rem 0; border-bottom: 1px solid #222; font-size: 0.85rem; }
    .metric-box {
        text-align: center; padding: 1rem; border-radius: 8px;
        background: #1a1a2e; margin: 0.3rem;
    }
    .metric-box .num { font-size: 1.8rem; font-weight: bold; color: #00d4ff; }
    .metric-box .label { font-size: 0.8rem; color: #888; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px 6px 0 0; }
</style>
""", unsafe_allow_html=True)


def init_session():
    defaults = {
        "result": None,
        "running": False,
        "topic": "",
        "history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>AutoResearch</h1>
        <p>基于多智能体协作的深度研究助手 — 输入主题，自动生成专业研究报告</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("## 系统配置")

        st.markdown("### 智能体架构")
        st.markdown("""
        ```
        用户输入 → Planner → Retriever/Analyst → Writer → 报告
                       ↑                              |
                       └──── 反思循环 ←───────────────┘
        ```
        """)

        st.markdown("### 核心组件")
        st.markdown("""
        - **PlannerAgent**: 任务分解与协调
        - **RetrieverAgent**: 网络/学术/本地检索
        - **AnalystAgent**: 深度分析与推理
        - **WriterAgent**: 结构化报告生成
        """)

        st.markdown("### 技术栈")
        st.markdown("""
        - LangGraph (工作流编排)
        - ChromaDB (向量数据库)
        - Sentence-Transformers (嵌入)
        - DuckDuckGo (网络搜索)
        - ArXiv API (学术检索)
        """)

        st.markdown("---")
        st.markdown("### 历史记录")
        if st.session_state.history:
            for h in st.session_state.history[-5:]:
                st.caption(f"- {h['topic'][:30]} ({h['time']})")
        else:
            st.caption("暂无历史记录")

        st.markdown("---")
        st.caption("AutoResearch v1.0 | 多智能体研究助手")


def render_metrics(result):
    if not result:
        return
    col1, col2, col3, col4 = st.columns(4)
    web_count = len(result.get("materials", {}).get("web_results", []))
    arxiv_count = len(result.get("materials", {}).get("arxiv_results", []))
    task_count = len(result.get("completed_tasks", []))
    report_len = len(result.get("report", ""))

    with col1:
        st.markdown(f'<div class="metric-box"><div class="num">{task_count}</div><div class="label">完成子任务</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><div class="num">{web_count}</div><div class="label">网络结果</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><div class="num">{arxiv_count}</div><div class="label">学术论文</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-box"><div class="num">{report_len}</div><div class="label">报告字数</div></div>', unsafe_allow_html=True)


def render_workflow_events(events):
    if not events:
        return
    st.markdown("### 工作流日志")
    agent_colors = {
        "PlannerAgent": "#ff9800",
        "RetrieverAgent": "#2196f3",
        "AnalystAgent": "#9c27b0",
        "WriterAgent": "#4caf50",
    }
    for evt in events:
        color = agent_colors.get(evt["agent"], "#888")
        st.markdown(
            f'<div class="log-item"><span style="color:{color};font-weight:bold">[{evt["agent"]}]</span> {evt["message"]}</div>',
            unsafe_allow_html=True,
        )


def render_plan(plan):
    if not plan:
        return
    st.markdown("### 研究计划")
    subtasks = plan.get("subtasks", [])
    for st_item in subtasks:
        agent_badge = f"🔵 检索" if st_item.get("agent") == "retriever" else "🟣 分析"
        st.markdown(f"**{st_item['id']}** {st_item['description']} {agent_badge}")

    keywords = plan.get("keywords", [])
    if keywords:
        st.markdown("**关键词**: " + " | ".join(keywords))


def run_research(topic: str):
    workflow = load_workflow()

    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.empty()

    all_events = []

    with st.spinner("系统初始化中..."):
        time.sleep(0.3)

    phases = [
        ("planning", "PlannerAgent", "制定研究计划...", 15),
        ("planning_done", "PlannerAgent", "计划制定完成", 20),
    ]

    result = workflow.run(topic)

    subtask_phases = []
    subtasks = result.get("plan", {}).get("subtasks", [])
    total_subtasks = len(subtasks) if subtasks else 1
    phase_step = 60 / total_subtasks

    for i, subtask in enumerate(subtasks):
        agent = subtask.get("agent", "retriever")
        agent_name = "RetrieverAgent" if agent == "retriever" else "AnalystAgent"
        progress = 20 + i * phase_step
        subtask_phases.append(("task_done", agent_name, f"[{subtask['id']}] {subtask['description']}", progress))

    phases.extend(subtask_phases)
    phases.extend([
        ("reflecting", "PlannerAgent", "质量反思与评估...", 85),
        ("writing", "WriterAgent", "撰写研究报告...", 95),
        ("done", "WriterAgent", "报告生成完成!", 100),
    ])

    for phase_type, agent, msg, prog in phases:
        progress_bar.progress(min(prog / 100.0, 1.0))
        status_text.text(f"[{agent}] {msg}")
        time.sleep(0.3)
        all_events.append({"type": phase_type, "agent": agent, "message": msg})
        with log_container.container():
            agent_colors = {
                "PlannerAgent": "#ff9800",
                "RetrieverAgent": "#2196f3",
                "AnalystAgent": "#9c27b0",
                "WriterAgent": "#4caf50",
            }
            color = agent_colors.get(agent, "#888")
            st.markdown(
                f'<div class="log-item"><span style="color:{color};font-weight:bold">[{agent}]</span> {msg}</div>',
                unsafe_allow_html=True,
            )

    result["events"] = all_events
    return result


# ── Main ──
init_session()
render_header()
render_sidebar()

# Input area
st.markdown("---")
col_input, col_btn = st.columns([4, 1])
with col_input:
    topic = st.text_input(
        "研究主题",
        placeholder="例如：Transformer在自动驾驶中的最新应用",
        value=st.session_state.topic,
        label_visibility="collapsed",
    )
with col_btn:
    run_btn = st.button("开始研究", type="primary", use_container_width=True)

if run_btn and topic.strip():
    st.session_state.topic = topic.strip()
    st.session_state.running = True
    result = run_research(topic.strip())
    st.session_state.result = result
    st.session_state.running = False
    st.session_state.history.insert(0, {
        "topic": topic.strip(),
        "time": datetime.now().strftime("%H:%M"),
    })
    st.rerun()

# Results display
if st.session_state.result:
    result = st.session_state.result

    st.markdown("---")
    render_metrics(result)
    st.markdown("---")

    tab_report, tab_plan, tab_materials, tab_workflow = st.tabs([
        "研究报告", "研究计划", "检索资料", "工作流日志"
    ])

    with tab_report:
        report = result.get("report", "暂无报告")
        st.markdown(report)

        st.download_button(
            label="下载 Markdown 报告",
            data=report,
            file_name=f"AutoResearch_{st.session_state.topic[:20]}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
        )

    with tab_plan:
        render_plan(result.get("plan", {}))

    with tab_materials:
        materials = result.get("materials", {})

        st.markdown("### 网络检索结果")
        for r in materials.get("web_results", [])[:8]:
            with st.expander(r.get("title", "N/A")):
                st.write(r.get("snippet", ""))
                st.caption(r.get("url", ""))

        st.markdown("### 学术论文")
        for p in materials.get("arxiv_results", [])[:5]:
            with st.expander(p.get("title", "N/A")):
                st.write(f"**作者**: {', '.join(p.get('authors', [])[:4])}")
                st.write(f"**发表**: {p.get('published', '')[:10]}")
                st.write(p.get("summary", ""))
                st.caption(p.get("link", ""))

        st.markdown("### 分析结果")
        for i, a in enumerate(result.get("analyses", []), 1):
            with st.expander(f"分析 {i}"):
                st.markdown(a)

    with tab_workflow:
        render_workflow_events(result.get("events", []))

elif not st.session_state.running:
    st.markdown("---")
    st.markdown("### 使用示例")
    examples = [
        "Transformer在自动驾驶中的最新应用",
        "大语言模型的Agent架构设计",
        "RAG技术的最新进展与挑战",
        "多智能体协作系统的设计模式",
        "量子计算在密码学中的应用",
    ]
    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with cols[i]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state.topic = ex
                st.rerun()

    st.markdown("""
    ---
    ### AutoResearch 架构概览

    ```
    ┌─────────────────────────────────────────────────────────┐
    │                    用户输入研究主题                       │
    └──────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────┐
    │               PlannerAgent (规划智能体)                  │
    │         • 任务分解  • 制定计划  • 反思优化                │
    └──────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
    │Retriever│      │  Analyst  │     │  Analyst  │
    │ Agent   │      │   Agent   │     │   Agent   │
    │ 网络检索 │      │  深度分析  │     │  逻辑推理  │
    │ ArXiv   │      │  数据处理  │     │  对比总结  │
    │ RAG     │      │           │     │           │
    └────┬────┘      └─────┬─────┘     └─────┬─────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────┐
    │               WriterAgent (写作智能体)                   │
    │         • 整合信息  • 结构化报告  • 引用管理              │
    └──────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────┐
    │                  生成完整研究报告                         │
    └─────────────────────────────────────────────────────────┘
    ```
    """)

if __name__ == "__main__":
    pass
