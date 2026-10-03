import re

from backend.config import get_llm
from backend.graph.state import ResearchState


def _fallback_revision_target(text: str) -> str:
    normalized = text.casefold()
    if any(term in normalized for term in ("citation", "reference", "bibliography")):
        return "citation"
    if any(term in normalized for term in ("search", "more sources", "additional evidence")):
        return "research"
    if any(term in normalized for term in ("retrieval", "local document", "missing evidence")):
        return "rag"
    return "analysis"


def critic_agent(state: ResearchState) -> ResearchState:

    analysis = state.get("analysis", "")
    context = state.get("retrieved_context", "")
    research_results = "\n\n".join(state.get("research_results", []))
    citations = "\n".join(state.get("citations", []))

    prompt = f"""
You are a strict research paper reviewer.

RESEARCH QUESTION:
{state.get("query", "")}

ANALYSIS:
{analysis}

LOCAL EVIDENCE:
{context}

EXTERNAL RESEARCH:
{research_results or "No external paper results were available."}

AVAILABLE REFERENCES:
{citations or "No references were generated."}

Check for:

1. Unsupported claims
2. Hallucinations
3. Missing citations
4. Contradictions
5. Weak conclusions

Return these fields exactly:
VERDICT: PASS or REVISION_REQUIRED
ISSUES: list each issue, or write "None"
NEXT_AGENT: research, rag, analysis, or citation

Then briefly explain the review. A report with no evidence must not pass.
"""

    response = get_llm().invoke(prompt)
    critique = str(response.content)
    verdict_match = re.search(
        r"^\s*VERDICT\s*:\s*(PASS|REVISION_REQUIRED|REVISE|FAIL)\b",
        critique,
        re.IGNORECASE | re.MULTILINE,
    )
    errors = list(state.get("errors", []))
    issues_match = re.search(
        r"^\s*ISSUES\s*:\s*(.*?)(?=^\s*NEXT_AGENT\s*:|^\s*REASON\s*:|\Z)",
        critique,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    if verdict_match:
        revision_required = verdict_match.group(1).upper() != "PASS"
    else:
        revision_required = True
        errors.append("Critic response did not contain a valid VERDICT; revision is required.")

    if issues_match:
        issues = [
            line.strip(" -*\t")
            for line in issues_match.group(1).splitlines()
            if line.strip() and line.strip().casefold() not in {"none", "n/a"}
        ]
    else:
        issues = []
    if revision_required and not issues:
        issues = ["The critic requested revision; review its critique for details."]
    has_evidence = bool(state.get("retrieved_documents")) or any(
        source.get("abstract") for source in state.get("sources", [])
    )
    if not has_evidence:
        revision_required = True
        issue = "No supporting source text or research-paper abstracts were available."
        if issue not in issues:
            issues.append(issue)

    target_match = re.search(
        r"^\s*NEXT_AGENT\s*:\s*(research|rag|analysis|citation)\b",
        critique,
        re.IGNORECASE | re.MULTILINE,
    )
    revision_target = (
        target_match.group(1).lower()
        if target_match
        else _fallback_revision_target("\n".join(issues) + "\n" + critique)
    )
    if "No supporting source text or research-paper abstracts were available." in issues:
        revision_target = "research"
    score_match = re.search(r"\b(?:QUALITY_SCORE|SCORE)\s*:\s*(\d+(?:\.\d+)?)", critique, re.I)
    quality_score = float(score_match.group(1)) if score_match else None

    return {
        "critique": critique,
        "issues": issues,
        "revision_required": revision_required,
        "revision_target": revision_target,
        "revision_step": 0,
        "iteration": max(0, int(state.get("iteration", 0)))
        + (1 if revision_required else 0),
        "quality_score": quality_score,
        "errors": errors,
        "workflow_status": "revision_required" if revision_required else "approved",
    }