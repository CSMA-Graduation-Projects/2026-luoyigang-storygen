import json
from typing import Any, Dict, List, Optional

from app.agents.splitter_agent import create_splitter_agent
from app.agents.pm_agent import create_pm_agent
from app.agents.qa_agent import create_qa_agent
from app.agents.architect_agent import create_architect_agent
from app.agents.code_analyzer_agent import create_code_analyzer_agent

from app.services.invest_score import calculate_invest_score_hybrid
from app.config import get_model_client
from app.services.history_service import save_history


def _sse(data: Dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# 百分制阈值
def need_improve(score, threshold=60):
    return score < threshold


async def stream_user_stories(requirement: str, save_to_history: bool = True):
    """文本需求生成用户故事，并在流程完成后写入 MongoDB 历史集合。"""

    get_model_client()  # 保持原有模型初始化行为

    events: List[Dict[str, Any]] = []
    sub_requirements: List[str] = []
    final_stories: List[str] = []
    invest_records: List[Dict[str, Any]] = []

    async def emit(data: Dict[str, Any]):
        events.append(data)
        return _sse(data)

    yield await emit({'type': 'start'})

    splitter = create_splitter_agent()
    split_result = await splitter.run(task=requirement)

    split_text = split_result.messages[-1].content
    sub_requirements = [
        line.strip("- ").strip()
        for line in split_text.split("\n")
        if line.strip()
    ]
    yield await emit({'type': 'split', 'data': sub_requirements})

    for req in sub_requirements:
        yield await emit({'type': 'sub_requirement', 'data': req})

        pm = create_pm_agent()
        qa = create_qa_agent()
        arch = create_architect_agent()

        current_input = req
        max_round = 3
        story = ""
        score = 0

        for round_idx in range(max_round):
            yield await emit({'type': 'round', 'data': round_idx + 1})

            pm_result = await pm.run(task=current_input)
            story = pm_result.messages[-1].content
            yield await emit({'type': 'pm', 'data': story})

            qa_result = await qa.run(task=story)
            qa_feedback = qa_result.messages[-1].content
            yield await emit({'type': 'qa', 'data': qa_feedback})

            arch_result = await arch.run(task=story)
            arch_feedback = arch_result.messages[-1].content
            yield await emit({'type': 'architect', 'data': arch_feedback})

            result = await calculate_invest_score_hybrid(story, 0.4)
            score = result["final_score"]

            invest_data = {
                'type': 'invest',
                'Independent': result["Independent"],
                'Negotiable': result["Negotiable"],
                'Valuable': result["Valuable"],
                'Estimable': result["Estimable"],
                'Small': result["Small"],
                'Testable': result["Testable"],
                'final_score': result["final_score"],
                'reason': result["reason"],
                'sub_requirement': req,
                'round': round_idx + 1,
            }
            invest_records.append(invest_data)
            yield await emit(invest_data)

            final_data = {
                'type': 'final',
                'data': story,
                'score': score,
                'sub_requirement': req,
            }

            if not need_improve(score):
                final_stories.append(story)
                yield await emit(final_data)
                break

            current_input = f"""
请基于以下信息优化用户故事：

【原始用户故事】
{story}

【QA反馈】
{qa_feedback}

【架构师反馈】
{arch_feedback}

【INVEST评分】
最终得分：{result["final_score"]}/100
Independent: {result["Independent"]},
Negotiable: {result["Negotiable"]},
Valuable: {result["Valuable"]},
Estimable: {result["Estimable"]},
Small: {result["Small"]},
Testable: {result["Testable"]},
reason: {result["reason"]},

【改进要求】
1. 优先优化低分维度（如 Independent / Testable 等）
2. 保证用户故事结构清晰：
   - 用户故事（As a / I want / So that）
   - 验收标准（Given-When-Then）
3. 提高可测试性与独立性
4. 避免模糊描述（如“提升体验”）

请输出优化后的完整用户故事（不要解释）。
"""

            yield await emit({'type': 'revise'})

        else:
            final_data = {
                'type': 'final',
                'data': story,
                'score': score,
                'sub_requirement': req,
            }
            final_stories.append(story)
            yield await emit(final_data)

    if save_to_history:
        history_id = save_history("text", {
            "title": requirement[:80] or "文本需求生成用户故事",
            "requirement": requirement,
            "summary": f"文本需求拆分为 {len(sub_requirements)} 条子需求，生成 {len(final_stories)} 条用户故事。",
            "sub_requirements": sub_requirements,
            "final_stories": final_stories,
            "invest_records": invest_records,
            "events": events,
            "statistics": {
                "requirement_count": len(sub_requirements),
                "story_count": len(final_stories),
                "event_count": len(events),
            },
        })
        yield await emit({'type': 'history_saved', 'history_id': history_id})

    yield await emit({'type': 'done'})


async def analyze_code_to_requirement(code: str, language: str = "unknown"):
    """将源代码逆向分析为自然语言需求描述，作为用户故事生成的输入。"""
    code_analyzer = create_code_analyzer_agent()

    task = f"""
请分析以下 {language} 代码，并将其转换为可用于生成用户故事的需求描述。

【代码内容】
```{language}
{code}
```
"""

    result = await code_analyzer.run(task=task)
    return result.messages[-1].content


async def stream_user_stories_from_code(code: str, language: str = "unknown"):
    """代码生成用户故事，并写入 MongoDB 的 code_story_history 集合。"""

    events: List[Dict[str, Any]] = []
    sub_requirements: List[str] = []
    final_stories: List[str] = []
    invest_records: List[Dict[str, Any]] = []
    code_analysis = ""

    def record_from_event(data: Dict[str, Any]):
        events.append(data)
        if data.get("type") == "split" and isinstance(data.get("data"), list):
            sub_requirements[:] = data["data"]
        elif data.get("type") == "final":
            final_stories.append(data.get("data", ""))
        elif data.get("type") == "invest":
            invest_records.append(data)

    start_event = {'type': 'start'}
    record_from_event(start_event)
    yield _sse(start_event)

    code_analysis = await analyze_code_to_requirement(code, language)
    analysis_event = {'type': 'code_analysis', 'data': code_analysis}
    record_from_event(analysis_event)
    yield _sse(analysis_event)

    async for event in stream_user_stories(code_analysis, save_to_history=False):
        # event 形如 data: {...}\n\n，这里解析一次用于保存代码历史
        try:
            data_text = event.strip().replace("data:", "", 1).strip()
            data = json.loads(data_text)
            if data.get("type") not in {"start", "done"}:
                record_from_event(data)
        except Exception:
            pass
        yield event

    history_id = save_history("code", {
        "title": f"{language or 'unknown'} 代码生成用户故事",
        "language": language,
        "code": code,
        "code_preview": code[:500],
        "code_analysis": code_analysis,
        "summary": f"代码分析后拆分为 {len(sub_requirements)} 个功能点，生成 {len(final_stories)} 条用户故事。",
        "sub_requirements": sub_requirements,
        "final_stories": final_stories,
        "invest_records": invest_records,
        "events": events,
        "statistics": {
            "requirement_count": len(sub_requirements),
            "story_count": len(final_stories),
            "event_count": len(events),
        },
    })
    yield _sse({'type': 'history_saved', 'history_id': history_id})
