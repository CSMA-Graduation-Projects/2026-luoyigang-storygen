import re
import json
from typing import final

from app.agents.appraiser_agent import create_appraiser_agent

# ------------------------
# 1. 规则评分
# ------------------------
def rule_based_score(story: str):
    score = 0
    details = {}

    text = story.lower()

    # I - Independent
    independent = not any(word in text for word in ["和", "以及", "并且", "同时"])
    details["Independent"] = int(independent)
    score += details["Independent"]

    # N - Negotiable
    negotiable = not any(word in text for word in ["必须", "一定要", "只能"])
    details["Negotiable"] = int(negotiable)
    score += details["Negotiable"]

    # V - Valuable
    valuable = "so that" in text or "以便" in text or "从而" in text
    details["Valuable"] = int(valuable)
    score += details["Valuable"]

    # E - Estimable
    estimable = 20 < len(story) < 1500
    details["Estimable"] = int(estimable)
    score += details["Estimable"]

    # S - Small
    lines = [l for l in story.split("\n") if l.strip()]
    small = len(lines) <= 1500
    details["Small"] = int(small)
    score += details["Small"]

    # T - Testable
    testable = "验收标准" in story or any(k in text for k in ["given", "when", "then"])
    details["Testable"] = int(testable)
    score += details["Testable"]

    return score, details


# 2. LLM评分
async def llm_based_score(story: str):
    agent = create_appraiser_agent()

    response = await agent.run(task=story)
    try:
        content = response.messages[-1].content
        data = json.loads(content)

        scores = {k: int(data[k]) for k in [
            "Independent", "Negotiable", "Valuable",
            "Estimable", "Small", "Testable"
        ]}

        total = sum(scores.values())
        reason = data.get("reason", "")

        return total, scores, reason

    except Exception:
        return 0, {}, "LLM评分解析失败"



# 3. 混合评分
async def calculate_invest_score_hybrid(story: str,rule_a: float):
    rule_score, rule_details = rule_based_score(story)#规则评分
    llm_score, llm_details, reason = await llm_based_score(story)#大语言模型评分
    #总评分
    final_scores = {
        "reason": reason,
        "final_score": int((rule_score/6*rule_a+llm_score/30*(1-rule_a))*50),
        "Independent": int((rule_details["Independent"]/6*rule_a+llm_details["Independent"]/30*(1-rule_a))*50),
        "Negotiable": int((rule_details["Negotiable"]/6*rule_a+llm_details["Negotiable"]/30*(1-rule_a))*50),
        "Valuable": int((rule_details["Valuable"]/6*rule_a+llm_details["Valuable"]/30*(1-rule_a))*50),
        "Estimable": int((rule_details["Estimable"]/6*rule_a+llm_details["Estimable"]/30*(1-rule_a))*50),
        "Small": int((rule_details["Small"]/6*rule_a+llm_details["Small"]/30*(1-rule_a))*50),
        "Testable": int((rule_details["Testable"]/6*rule_a+llm_details["Testable"]/30*(1-rule_a))*50)
    }

    return final_scores