from backend.graph.state import ResearchState
from backend.tools.citation_tool import build_citation_index


def citation_agent(state: ResearchState) -> ResearchState:
    citations, citation_map = build_citation_index(
        state.get("sources", []),
        state.get("retrieved_sources", []),
    )
    return {
        "citations": citations,
        "citation_map": citation_map,
    }