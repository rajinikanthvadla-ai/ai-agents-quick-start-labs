from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from bedrock_client import ask_bedrock


class AgentState(TypedDict):
    issue: str
    analysis: str
    action: str
    verification: str


def analyze_issue(state: AgentState):
    prompt = f"""
Analyze this DevOps issue.

Issue:
{state["issue"]}

Return a short technical analysis.
"""

    analysis = ask_bedrock(
        prompt=prompt,
        system_prompt="You are a DevOps workflow agent. Be concise and practical.",
        max_tokens=400,
    )

    return {"analysis": analysis}


def recommend_action(state: AgentState):
    prompt = f"""
Based on this analysis, recommend the next action.

Analysis:
{state["analysis"]}

Return the best immediate action for an on-call engineer.
"""

    action = ask_bedrock(
        prompt=prompt,
        system_prompt="You recommend safe DevOps incident actions.",
        max_tokens=400,
    )

    return {"action": action}


def verify_action(state: AgentState):
    prompt = f"""
Create a verification checklist for this action.

Action:
{state["action"]}

Return 3 to 5 checks that prove the service recovered.
"""

    verification = ask_bedrock(
        prompt=prompt,
        system_prompt="You create practical production verification steps.",
        max_tokens=400,
    )

    return {"verification": verification}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze_issue", analyze_issue)
    graph.add_node("recommend_action", recommend_action)
    graph.add_node("verify_action", verify_action)

    graph.add_edge(START, "analyze_issue")
    graph.add_edge("analyze_issue", "recommend_action")
    graph.add_edge("recommend_action", "verify_action")
    graph.add_edge("verify_action", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        {
            "issue": "checkout API latency is very high after deployment",
            "analysis": "",
            "action": "",
            "verification": "",
        }
    )

    print("\nAnalysis:")
    print(result["analysis"])
    print("\nAction:")
    print(result["action"])
    print("\nVerification:")
    print(result["verification"])


if __name__ == "__main__":
    main()
