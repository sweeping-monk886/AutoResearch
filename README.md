# AutoResearch — 基于多智能体协作的深度研究助手

一个能自主完成深度研究报告的多智能体系统。用户只需输入研究主题（如"Transformer在自动驾驶中的最新应用"），系统即可自动规划、检索、分析、综合并生成一份结构完整的专业研究报告。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-red)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-green?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 系统架构

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

## 技术栈

| 类别 | 技术 |
|------|------|
| 核心框架 | LangGraph (工作流编排) |
| 大模型 | OpenAI / Qwen / DeepSeek API |
| 向量数据库 | ChromaDB |
| 嵌入模型 | Sentence-Transformers (all-MiniLM-L6-v2) |
| 网络搜索 | DuckDuckGo API |
| 学术检索 | ArXiv API |
| Web界面 | Streamlit |
| 语言 | Python 3.10+ |

## 核心功能

1. **智能任务规划** — PlannerAgent 自动分解研究主题为可执行子任务
2. **多源信息检索** — 支持网络搜索、ArXiv学术论文、本地知识库RAG
3. **深度内容分析** — AnalystAgent 进行文本分析、关键发现提取
4. **自动化报告生成** — WriterAgent 整合所有信息生成结构化报告
5. **反思与优化** — 系统自动评估报告质量并进行迭代优化
6. **可视化工作流** — 实时展示多智能体协作过程

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/AutoResearch.git
cd AutoResearch
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 5. 启动应用

```bash
# 方式一：直接启动
streamlit run app.py

# 方式二：通过主入口
python main.py
```

浏览器自动打开 `http://localhost:8501`

## 项目结构

```
AutoResearch/
├── app.py                  # Streamlit Web界面
├── main.py                 # 主入口
├── config/
│   ├── __init__.py
│   └── settings.py         # 全局配置
├── agents/
│   ├── __init__.py
│   ├── planner.py          # 规划智能体
│   ├── retriever.py        # 检索智能体
│   ├── analyst.py          # 分析智能体
│   ├── writer.py           # 写作智能体
│   └── workflow.py         # LangGraph工作流
├── tools/
│   ├── __init__.py
│   ├── search_tool.py      # 网络搜索工具
│   ├── rag_tool.py         # RAG检索工具
│   └── analysis_tool.py    # 分析工具
├── utils/
│   └── __init__.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 面试展示要点

### 技术亮点

1. **Agent架构设计**: 主从式多智能体协作，Planner-Worker模式
2. **RAG技术**: ChromaDB向量数据库 + Sentence-Transformers嵌入 + 语义检索
3. **工作流编排**: 基于LangGraph的状态机设计，支持条件分支和反思循环
4. **多源检索**: 网络搜索 + ArXiv学术检索 + 本地知识库三路融合
5. **Prompt工程**: 为每个Agent设计专用System Prompt
6. **反思机制**: PlannerAgent对报告质量进行自动评估和迭代优化

### 设计决策

- **为什么选LangGraph**: 相比纯LangChain，LangGraph提供更灵活的状态管理和条件流转
- **为什么用ChromaDB**: 轻量级本地部署，无需外部服务，适合原型验证
- **为什么三路检索**: 覆盖时效性(网络)、权威性(ArXiv)、私有知识(RAG)

### 遇到的挑战与解决方案

1. **Agent幻觉**: 通过RAG提供事实依据，减少虚构内容
2. **协调死锁**: 使用状态机明确流转条件，避免循环依赖
3. **信息过载**: 在检索阶段设置Top-K限制，分析阶段聚焦关键信息

## 部署到 GitHub

### 步骤 1: 创建 GitHub 仓库

1. 登录 GitHub，点击右上角 `+` → `New repository`
2. 仓库名: `AutoResearch`
3. 描述: `基于多智能体协作的深度研究助手`
4. 选择 **Public**
5. 不要初始化 README（我们本地已有）
6. 点击 `Create repository`

### 步骤 2: 推送代码

```bash
cd AutoResearch
git init
git add .
git commit -m "feat: 初始化AutoResearch多智能体研究助手"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AutoResearch.git
git push -u origin main
```

### 步骤 3: 部署到 HuggingFace Spaces (免费在线访问)

1. 注册 [HuggingFace](https://huggingface.co) 账号
2. 点击 `New Space`
3. 选择 `Streamlit` 作为 SDK
4. 设置 Space 名称为 `AutoResearch`
5. 在 Settings → Repository secrets 中添加 `OPENAI_API_KEY`
6. 上传项目文件或连接 GitHub 仓库
7. Space 会自动构建并部署

### 步骤 4: 添加 GitHub Topics

在仓库 Settings → General → Topics 中添加：

```
ai-agent multi-agent rag langchain langgraph streamlit research assistant
```

## 使用示例

输入研究主题后，系统会自动：

1. **规划阶段**: 分解为 6 个子任务（背景检索、论文检索、技术分析、应用分析、趋势分析、对比总结）
2. **检索阶段**: 从网络、ArXiv、本地知识库三路检索信息
3. **分析阶段**: 对检索结果进行深度分析，提取关键发现
4. **反思阶段**: 评估信息充分性，必要时补充检索
5. **写作阶段**: 生成包含摘要、背景、技术现状、关键发现、对比分析、趋势、结论、参考文献的完整报告

## License

MIT License

## 作者

你的名字 — 你的GitHub主页链接
