import re

from backend.config import get_llm
from backend.graph.state import ResearchState
from backend.tools.paper_search import search_papers
from backend.tools.web_search import search_arxiv


def _extract_search_queries(research_plan: str) -> list[str]:
    section = re.search(
        r"^\s*\d+\.\s*SEARCH QUERIES\b(.*?)(?=^\s*\d+\.|\Z)",
        research_plan,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    if not section:
        return []

    queries = []
    for line in section.group(1).splitlines():
        query = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip().strip('"')
        if query and query.casefold() not in {item.casefold() for item in queries}:
            queries.append(query)
    return queries[:2]


def research_agent(state: ResearchState) -> ResearchState:
    query = state["query"]
    sources = []
    results = []
    errors = list(state.get("errors", []))

    for provider, search in (("Crossref", search_papers), ("arXiv", search_arxiv)):
        try:
            papers = search(query, limit=5)
        except (RuntimeError, ValueError) as exc:
            errors.append(str(exc))
            continue

        prefix = "P" if provider == "Crossref" else "A"
        for index, paper in enumerate(papers, start=1):
            source_id = f"{prefix}{index}"
            source = {**paper, "source_id": source_id}
            sources.append(source)
            summary = paper.get("abstract") or "No abstract was provided by the source."
            results.append(
                f"[{source_id}] {paper['title']} ({paper.get('published', 'date unavailable')})\n"
                f"Authors: {', '.join(paper.get('authors', [])) or 'not listed'}\n"
                f"Source: {paper.get('url', '')}\n"
                f"Abstract: {summary[:3000]}"
            )

    prompt = f"""
You are the Research Agent of ResearchPilot AI,
an autonomous academic research assistant.

The user wants to research:

{query}

Search results from Crossref and arXiv:
{chr(10).join(results) if results else "No external paper search results were available."}

Your job is to create a detailed research plan.

Return the following:

1. MAIN RESEARCH QUESTION
Rewrite the user's question clearly.

2. RESEARCH OBJECTIVES
List 3-5 objectives.

3. KEY SUBTOPICS
Identify the important areas that must be investigated.

4. SEARCH QUERIES
Generate 5-10 useful academic search queries.

5. REQUIRED EVIDENCE
Explain what type of evidence should be collected.

6. IMPORTANT CONCEPTS
List important technical terms, methods, models, or theories.

7. POSSIBLE RESEARCH GAPS
Identify areas that should be investigated for potential gaps.

8. EXPECTED OUTPUT
Explain what the final research report should contain.

Important rules:
- Do not invent papers or references.
- Do not claim something is true without evidence.
- This is a research plan, not the final answer.
"""

    research_plan = str(get_llm().invoke(prompt).content)
    search_queries = _extract_search_queries(research_plan)
    seen_papers = {
        source.get("doi") or source.get("url") or source.get("title", "").casefold()
        for source in sources
    }

    for search_query in search_queries:
        for provider, search in (("Crossref", search_papers), ("arXiv", search_arxiv)):
            try:
                papers = search(search_query, limit=3)
            except (RuntimeError, ValueError) as exc:
                message = str(exc)
                if message not in errors:
                    errors.append(message)
                continue

            prefix = "P" if provider == "Crossref" else "A"
            existing_count = sum(
                source.get("source_id", "").startswith(prefix) for source in sources
            )
            for paper in papers:
                identity = (
                    paper.get("doi")
                    or paper.get("url")
                    or paper.get("title", "").casefold()
                )
                if identity in seen_papers:
                    continue

                seen_papers.add(identity)
                source_id = f"{prefix}{existing_count + 1}"
                existing_count += 1
                source = {**paper, "source_id": source_id}
                sources.append(source)
                summary = paper.get("abstract") or "No abstract was provided by the source."
                results.append(
                    f"[{source_id}] {paper['title']} "
                    f"({paper.get('published', 'date unavailable')})\n"
                    f"Authors: {', '.join(paper.get('authors', [])) or 'not listed'}\n"
                    f"Source: {paper.get('url', '')}\n"
                    f"Abstract: {summary[:3000]}"
                )

    return {
        "research_plan": research_plan,
        "research_results": results,
        "sources": sources,
        "search_queries": [query, *search_queries],
        "errors": errors,
    }