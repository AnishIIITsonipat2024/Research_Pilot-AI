from backend.config import get_llm
from backend.graph.state import ResearchState


def analysis_agent(state: ResearchState) -> ResearchState:

    query = state["query"]
    context = state.get("retrieved_context", "")
    research_results = "\n\n".join(state.get("research_results", []))

    prompt = f"""
You are a research analysis agent.

Research question:
{query}

Evidence:

{context}

External research:

{research_results or "No external paper abstracts are available."}

Analyze the evidence.

Identify:
- Important findings
- Methods
- Results
- Limitations
- Research gaps
- Conflicting evidence

Return a concise KEY FINDINGS list after your analysis.
Do not invent information. Attribute factual claims to source IDs when possible.
Clearly distinguish retrieved evidence from interpretation, and state when evidence is missing.
"""

    response = get_llm().invoke(prompt)
    analysis = str(response.content)
    key_findings = [
        line.strip(" -*\t")
        for line in analysis.splitlines()
        if line.strip().startswith(("-", "*"))
    ]

    return {
        "analysis": analysis,
        "key_findings": key_findings,
    }