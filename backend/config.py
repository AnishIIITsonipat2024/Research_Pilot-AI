import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
VECTORSTORE_PATH = os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db"),
)


def get_llm(temperature: float = 0):
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Set it in the environment or project .env file."
        )

    from langchain_groq import ChatGroq

    return ChatGroq(
        model=MODEL_NAME,
        temperature=temperature,
        api_key=GROQ_API_KEY,
    )