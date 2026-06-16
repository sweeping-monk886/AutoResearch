from typing import Dict, Any, List, TypedDict, Literal
from dataclasses import dataclass, field
from config.settings import Settings
from agents.planner import PlannerAgent
from agents.retriever import RetrieverAgent
from agents.analyst import AnalystAgent
from agents.writer import WriterAgent


class ResearchState(TypedDict):
    topic: str
    plan: Dict[str, Any]
    current_task_idx: int
    completed_tasks: List[str]
    task_results: Dict[str, Any]
    analyses: List[str]
    materials: Dict[str, Any]
    report: str
    phase: Literal["planning", "retrieving", "analyzing", "writing", "reflecting", "done"]
    reflection_count: int
    logs: List[Dict[str, str]]


@dataclass
class WorkflowEvent:
    type: str
    agent: str
    message: str
    data: Any = None


class ResearchWorkflow:
    """基于状态机的多智能体研究工作流，用LangGraph理念设计。"""

    def __init__(self, settings: Settings = None, llm_call=None):
        self.settings = settings or Settings()
        self.planner = PlannerAgent(llm_call=llm_call)
        self.retriever = RetrieverAgent(self.settings)
        self.analyst = AnalystAgent(llm_call=llm_call)
        self.writer = WriterAgent(llm_call=llm_call)
        self.llm_call = llm_call
        self.events: List[WorkflowEvent] = []

    def run(self, topic: str) -> Dict[str, Any]:
        state = ResearchState(
            topic=topic,
            plan={},
            current_task_idx=0,
            completed_tasks=[],
            task_results={},
            analyses=[],
            materials={},
            report="",
            phase="planning",
            reflection_count=0,
            logs=[],
        )
        self.events.clear()

        # Phase 1: Planning
        state = self._phase_planning(state)

        # Phase 2: Retrieve & Analyze loop
        state = self._phase_execute(state)

        # Phase 3: Reflect
        state = self._phase_reflect(state)

        # Phase 4: Write report
        state = self._phase_writing(state)

        return {
            "topic": state["topic"],
            "plan": state["plan"],
            "materials": state["materials"],
            "analyses": state["analyses"],
            "report": state["report"],
            "events": [
                {"type": e.type, "agent": e.agent, "message": e.message}
                for e in self.events
            ],
            "completed_tasks": state["completed_tasks"],
        }

    def run_streaming(self, topic: str):
        """生成器模式，逐步产出事件。"""
        state = ResearchState(
            topic=topic, plan={}, current_task_idx=0, completed_tasks=[],
            task_results={}, analyses=[], materials={}, report="",
            phase="planning", reflection_count=0, logs=[],
        )
        self.events.clear()

        yield ("planning", "PlannerAgent", "正在分析研究主题并制定计划...")

        state = self._phase_planning(state)
        yield ("planning_done", "PlannerAgent", f"计划已制定，共 {len(state['plan'].get('subtasks', []))} 个子任务")

        for i, subtask in enumerate(state["plan"].get("subtasks", [])):
            task_id = subtask["id"]
            desc = subtask["description"]
            agent = subtask.get("agent", "retriever")

            yield ("task_start", agent, f"[{task_id}] {desc}")

            if agent == "retriever":
                result = self.retriever.retrieve(task_id, desc, state["plan"].get("keywords", []))
                state["task_results"][task_id] = result
                state["materials"] = self._merge_materials(state["materials"], result)
                state["completed_tasks"].append(task_id)
                yield ("task_done", "RetrieverAgent", f"[{task_id}] 检索完成，获取 {len(result.get('web_results', []))} 条网络结果, {len(result.get('arxiv_results', []))} 篇论文")
            elif agent == "analyst":
                ctx = state["materials"].get("combined_text", "")
                result = self.analyst.analyze(task_id, desc, ctx)
                state["task_results"][task_id] = result
                state["analyses"].append(result.get("analysis", ""))
                state["completed_tasks"].append(task_id)
                yield ("task_done", "AnalystAgent", f"[{task_id}] 分析完成")

        # Reflect
        yield ("reflecting", "PlannerAgent", "正在进行质量反思...")
        reflection = self.planner.reflect(
            state["topic"], state["completed_tasks"], state["materials"].get("combined_text", "")
        )
        yield ("reflect_done", "PlannerAgent", f"质量评分: {reflection.get('quality_score', 0)}/100, 信息充分: {reflection.get('is_sufficient', False)}")

        # Write
        yield ("writing", "WriterAgent", "正在撰写研究报告...")
        state["report"] = self.writer.write(
            state["topic"],
            state["plan"].get("report_outline", []),
            state["materials"],
            state["analyses"],
        )
        yield ("done", "WriterAgent", "报告生成完成")

        return {
            "topic": state["topic"],
            "plan": state["plan"],
            "materials": state["materials"],
            "analyses": state["analyses"],
            "report": state["report"],
            "events": [{"type": e.type, "agent": e.agent, "message": e.message} for e in self.events],
            "completed_tasks": state["completed_tasks"],
        }

    def _phase_planning(self, state: ResearchState) -> ResearchState:
        plan = self.planner.create_plan(state["topic"])
        state["plan"] = plan
        state["phase"] = "planning"
        self._emit("planning", "PlannerAgent", f"已制定研究计划，共 {len(plan['subtasks'])} 个子任务")
        return state

    def _phase_execute(self, state: ResearchState) -> ResearchState:
        subtasks = state["plan"].get("subtasks", [])
        for subtask in subtasks:
            task_id = subtask["id"]
            desc = subtask["description"]
            agent = subtask.get("agent", "retriever")

            self._emit("task_start", agent, f"执行 [{task_id}]: {desc}")

            if agent == "retriever":
                state["phase"] = "retrieving"
                result = self.retriever.retrieve(task_id, desc, state["plan"].get("keywords", []))
                state["task_results"][task_id] = result
                state["materials"] = self._merge_materials(state["materials"], result)
                self._emit("task_done", "RetrieverAgent", f"[{task_id}] 检索完成")
            elif agent == "analyst":
                state["phase"] = "analyzing"
                ctx = state["materials"].get("combined_text", "")
                result = self.analyst.analyze(task_id, desc, ctx)
                state["task_results"][task_id] = result
                state["analyses"].append(result.get("analysis", ""))
                self._emit("task_done", "AnalystAgent", f"[{task_id}] 分析完成")

            state["completed_tasks"].append(task_id)
        return state

    def _phase_reflect(self, state: ResearchState) -> ResearchState:
        state["phase"] = "reflecting"
        reflection = self.planner.reflect(
            state["topic"], state["completed_tasks"], state["materials"].get("combined_text", "")
        )
        self._emit("reflection", "PlannerAgent",
                    f"质量评分: {reflection.get('quality_score', 0)}/100")
        state["reflection_count"] += 1
        return state

    def _phase_writing(self, state: ResearchState) -> ResearchState:
        state["phase"] = "writing"
        state["report"] = self.writer.write(
            state["topic"],
            state["plan"].get("report_outline", []),
            state["materials"],
            state["analyses"],
        )
        state["phase"] = "done"
        self._emit("report_done", "WriterAgent", "报告生成完成")
        return state

    def _merge_materials(self, existing: Dict, new: Dict) -> Dict:
        merged = dict(existing)
        for key in ["web_results", "arxiv_results", "fetched_pages"]:
            merged.setdefault(key, [])
            merged[key].extend(new.get(key, []))
        rag_new = new.get("rag_results", [])
        if rag_new:
            merged.setdefault("rag_results", [])
            merged["rag_results"].extend(rag_new)
        old_text = merged.get("combined_text", "")
        new_text = new.get("combined_text", "")
        if old_text and new_text:
            merged["combined_text"] = old_text + "\n\n---\n\n" + new_text
        elif new_text:
            merged["combined_text"] = new_text
        return merged

    def _emit(self, etype: str, agent: str, message: str):
        self.events.append(WorkflowEvent(type=etype, agent=agent, message=message))
