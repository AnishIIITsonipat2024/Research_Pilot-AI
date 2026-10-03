def build_citation_index(
    sources: list[dict],
    retrieved_sources: list[dict],
) -> tuple[list[str], dict[str, dict]]:
    citation_map = {}
    citations = []
    for source in sources:
        source_id = source.get("source_id")
        if not source_id:
            continue
        citation_map[source_id] = source
        authors = ", ".join(source.get("authors", [])) or "Author not listed"
        year = source.get("published") or "n.d."
        citations.append(
            f"[{source_id}] {authors} ({year}). {source.get('title', 'Untitled')}."
        )

    for retrieved_source in retrieved_sources:
        source = dict(retrieved_source)
        source_id = source.get("source_id")
        if not source_id:
            source_id = f"R{len(citation_map) + 1}"
            source["source_id"] = source_id

        citation_map[source_id] = source
        title = source.get("title") or source.get("source") or "Local document"
        page = source.get("page")
        page_reference = f", p. {page + 1}" if isinstance(page, int) else ""
        citations.append(f"[{source_id}] {title}{page_reference}.")

    return citations, citation_map
