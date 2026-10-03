from backend.rag.retriever import get_retriever
from backend.graph.state import ResearchState


def rag_agent(state: ResearchState) -> ResearchState:
    query = state["query"]
    retriever = get_retriever()
    documents = retriever.invoke(query)
    retrieved_sources = []
    retrieved_documents = []
    context_parts = []

    for index, document in enumerate(documents, start=1):
        metadata = dict(document.metadata)
        metadata.setdefault("source", "Local document")
        metadata["source_id"] = f"R{index}"
        retrieved_sources.append(metadata)
        retrieved_documents.append(document.page_content)
        context_parts.append(
            f"[R{index}] SOURCE: {metadata}\nCONTENT:\n{document.page_content}"
        )

    context = "\n\n".join(context_parts)
    if not context:
        context = (
            "No matching local documents were found. External research results, if any, "
            "are listed separately."
        )

    return {
        "documents": retrieved_documents,
        "retrieved_documents": retrieved_documents,
        "retrieved_sources": retrieved_sources,
        "retrieved_context": context,
    }