import json
import re
from html import unescape
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def search_papers(query: str, limit: int = 5, timeout: float = 10) -> list[dict]:
    if not query.strip():
        raise ValueError("A non-empty query is required to search research papers.")

    limit = max(1, min(limit, 10))
    params = urlencode({"query.bibliographic": query, "rows": limit})
    request = Request(
        f"https://api.crossref.org/works?{params}",
        headers={"User-Agent": "ResearchPilotAI/1.0 (academic research assistant)"},
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Crossref paper search failed: {exc}") from exc

    papers = []
    for item in payload.get("message", {}).get("items", []):
        title = " ".join(item.get("title", [])).strip()
        if not title:
            continue

        authors = [
            " ".join(
                part for part in (author.get("given"), author.get("family")) if part
            )
            for author in item.get("author") or []
        ]
        date_parts = (
            item.get("published-print", {}).get("date-parts")
            or item.get("published-online", {}).get("date-parts")
            or []
        )
        published = "-".join(str(part) for part in date_parts[0]) if date_parts else ""
        abstract = unescape(item.get("abstract", ""))
        abstract = re.sub(r"<[^>]+>", " ", abstract)
        abstract = " ".join(abstract.split())
        doi = item.get("DOI", "")

        papers.append(
            {
                "title": title,
                "authors": authors,
                "published": published,
                "container_title": " ".join(item.get("container-title", [])).strip(),
                "abstract": abstract,
                "doi": doi,
                "url": item.get("URL") or (f"https://doi.org/{doi}" if doi else ""),
                "provider": "Crossref",
            }
        )
        if len(papers) >= limit:
            break

    return papers
