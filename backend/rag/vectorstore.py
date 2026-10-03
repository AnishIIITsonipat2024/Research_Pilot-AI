import hashlib

from langchain_chroma import Chroma

from backend.config import VECTORSTORE_PATH
from backend.rag.embeddings import get_embeddings


def create_vectorstore(documents):
    if not documents:
        raise ValueError("At least one document chunk is required for indexing.")
    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings,
    )
    ids = []
    for document in documents:
        identity = "\0".join(
            (
                str(document.metadata.get("source", "")),
                str(document.metadata.get("page", "")),
                document.page_content,
            )
        )
        ids.append(hashlib.sha256(identity.encode("utf-8")).hexdigest())

    vectorstore.add_documents(documents=documents, ids=ids)
    return vectorstore