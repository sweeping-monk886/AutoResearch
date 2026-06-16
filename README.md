# AutoResearch

做一个能自己做研究的AI Agent系统。给它一个主题，它会自己搜资料、读论文、分析整理、最后写成一份完整的研究报告。

一开始是想偷懒，每次看论文太费时间了，后来做着做着发现多Agent协作这块挺有意思的，就往深了做。

## 它能干嘛

输入一个研究主题，比如"Transformer在自动驾驶中的应用"，系统会：

1. 先拆解任务——要查哪些方面、用什么关键词搜
2. 同时从网络、ArXiv论文库、本地知识库三个渠道找资料
3. 对找到的内容做分析，提取关键信息
4. 最后把这些内容整理成一份有结构的研究报告，带参考文献

整个过程你能在网页上看到每个Agent在干什么。

## 架构

大概就是这么个流程：

```
用户输入主题
    ↓
PlannerAgent (拆任务、做计划、把控质量)
    ↓
RetrieverAgent ← → AnalystAgent
  (搜资料)         (分析整理)
    ↓
WriterAgent (写报告)
    ↓
输出研究报告
```

Planner是总指挥，负责把任务分下去，还要检查其他Agent干得怎么样，不行就让它们重做。

## 技术栈

- **LangGraph** — 工作流编排，用状态机控制Agent之间的流转
- **ChromaDB** — 向量数据库，做本地知识库的语义检索
- **Sentence-Transformers** — 文本嵌入，用的 `all-MiniLM-L6-v2`
- **DuckDuckGo** — 网络搜索，不需要API key
- **ArXiv API** — 搜学术论文
- **Streamlit** — 前端界面，写起来快
- **Python**

## 跑起来

```bash
git clone https://github.com/sweeping-monk886/AutoResearch.git
cd AutoResearch
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`。

如果你想接自己的大模型API（比如OpenAI或DeepSeek），在项目根目录创建 `.env` 文件：

```
OPENAI_API_KEY=你的key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

不接也行，系统会用模板模式跑，能演示整个流程，只是分析质量差一些。

## 项目结构

```
AutoResearch/
├── app.py              # Streamlit界面，主要入口
├── main.py             # 命令行启动脚本
├── agents/
│   ├── planner.py      # 规划Agent，任务分解+反思
│   ├── retriever.py    # 检索Agent，网络+论文+RAG
│   ├── analyst.py      # 分析Agent，文本分析+代码执行
│   ├── writer.py       # 写作Agent，报告生成
│   └── workflow.py     # 整个工作流的状态机
├── tools/
│   ├── search_tool.py  # 搜索工具（DuckDuckGo + ArXiv）
│   ├── rag_tool.py     # ChromaDB向量检索
│   └── analysis_tool.py # 文本分析+安全代码沙箱
├── config/
│   └── settings.py     # 配置文件
├── requirements.txt
└── .env.example
```

## 做的过程中遇到的一些坑

**Agent幻觉问题**：一开始Retriever搜回来的内容，Analyst分析的时候会自己编造一些不存在的数据。后来加了RAG作为事实校验，好了一些，但不能完全解决。

**Agent之间的协调**：最开始想让Agent互相通信，后来发现太复杂了，改成Planner统一调度，简单很多。状态机虽然不够灵活，但至少不会死锁。

**搜索结果质量**：DuckDuckGo搜出来的结果参差不齐，有些网页内容很水。后来加了网页正文抓取，过滤掉了纯标题党和导航页。

**ChromaDB首次加载慢**：第一次跑的时候Sentence-Transformers要下载模型，大概100多MB，之后就快了。

## 截图

<!-- TODO: 加一张界面截图 -->

## License

MIT
