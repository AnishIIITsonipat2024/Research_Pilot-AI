import xml.etree.ElementTree as ET
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ARXIV_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}


def search_arxiv(query: str, limit: int = 5, timeout: float = 10) -> list[dict]:
    if not query.strip():
        raise ValueError("A non-empty query is required to search arXiv.")

    limit = max(1, min(limit, 10))
    params = urlencode(
        {"search_query": f"all:{query}", "start": 0, "max_results": limit}
    )
    request = Request(
        f"https://export.arxiv.org/api/query?{params}",
        headers={"User-Agent": "ResearchPilotAI/1.0 (academic research assistant)"},
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            root = ET.fromstring(response.read())
    except (URLError, TimeoutError, ET.ParseError) as exc:
        raise RuntimeError(f"arXiv paper search failed: {exc}") from exc

    papers = []
    for entry in root.findall("atom:entry", ARXIV_NAMESPACE):
        title = " ".join((entry.findtext("atom:title", default="", namespaces=ARXIV_NAMESPACE)).split())
        if not title:
            continue

        authors = [
            author.findtext("atom:name", default="", namespaces=ARXIV_NAMESPACE)
            for author in entry.findall("atom:author", ARXIV_NAMESPACE)
        ]
        abstract = " ".join(
            entry.findtext("atom:summary", default="", namespaces=ARXIV_NAMESPACE).split()
        )
        papers.append(
            {
                "title": title,
                "authors": authors,
                "published": entry.findtext(
                    "atom:published", default="", namespaces=ARXIV_NAMESPACE
                )[:10],
                "abstract": abstract,
                "url": entry.findtext("atom:id", default="", namespaces=ARXIV_NAMESPACE),
                "provider": "arXiv",
            }
        )

    return papers
