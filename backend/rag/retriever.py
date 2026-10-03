from backend.rag.embeddings import get_embeddings
from backend.config import VECTORSTORE_PATH
from langchain_chroma import Chroma


def get_retriever():
    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": 5})