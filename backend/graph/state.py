from typing import Any, Dict, List, Optional, TypedDict


class ResearchState(TypedDict, total=False):

    # ==========================================
    # USER INPUT
    # ==========================================

    query: str


    # ==========================================
    # SUPERVISOR
    # ==========================================

    next_agent: str

    current_agent: str

    workflow_status: str

    iteration: int

    max_iterations: int

    revision_step: int

    revision_target: str

    use_local_documents: bool

    prioritize_local_documents: bool


    # ==========================================
    # RESEARCH AGENT
    # ==========================================

    research_plan: str

    research_results: List[str]

    sources: List[Dict[str, Any]]

    search_queries: List[str]


    # ==========================================
    # RAG AGENT
    # ==========================================

    documents: List[str]

    retrieved_documents: List[str]

    retrieved_context: str

    retrieved_sources: List[Dict[str, Any]]


    # ==========================================
    # ANALYSIS AGENT
    # ==========================================

    analysis: str

    key_findings: List[str]


    # ==========================================
    # CITATION AGENT
    # ==========================================

    citations: List[str]

    citation_map: Dict[str, Any]


    # ==========================================
    # CRITIC AGENT
    # ==========================================

    critique: str

    quality_score: Optional[float]

    issues: List[str]

    revision_required: bool


    # ==========================================
    # WRITER AGENT
    # ==========================================

    draft_report: str

    final_report: str


    # ==========================================
    # ERROR / DEBUGGING
    # ==========================================

    errors: List[str]