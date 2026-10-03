from backend.config import get_llm
from backend.graph.state import ResearchState


def writer_agent(state: ResearchState) -> ResearchState:

    query = state["query"]
    analysis = state.get("analysis", "")
    citations = "\n".join(state.get("citations", []))
    critique = state.get("critique", "")
    sources = state.get("citation_map", {})
    review_note = ""
    if state.get("revision_required"):
        issues = "\n".join(f"- {issue}" for issue in state.get("issues", []))
        review_note = (
            "\nThe critic did not approve this report before the iteration limit. "
            "Include a clearly labeled review caveat and list these unresolved issues:\n"
            f"{issues or critique}"
        )

    prompt = f"""
You are an academic research writer.

Research question:
{query}

Analysis:
{analysis}

Verified source references:
{sources}

Citation list:
{citations or "No verifiable citations are available."}

Most recent critique:
{critique or "No critique was provided."}

Write a research report containing:

# Title

## Abstract

## Introduction

## Literature Review

## Key Findings

## Research Gaps

## Limitations

## Future Research

## Conclusion

## References

Use only information supported by the supplied evidence and source map. Cite claims
using their exact source IDs (for example, [P1] or [R1]). Do not invent references.
Clearly state when evidence is limited or unavailable.{review_note}
"""

    response = get_llm().invoke(prompt)
    final_report = str(response.content)
    status = state.get("workflow_status", "completed")
    if status != "max_iterations_reached":
        status = "completed"

    return {
        "draft_report": final_report,
        "final_report": final_report,
        "workflow_status": status,
    }