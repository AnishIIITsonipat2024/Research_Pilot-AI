from backend.config import get_llm


def detect_hallucination(
    answer: str,
    evidence: str
):
    """
    Check whether an answer contains claims
    that are not supported by the retrieved evidence.
    """

    prompt = f"""
You are a hallucination detection system
for an academic research assistant.

ANSWER:
{answer}

AVAILABLE EVIDENCE:
{evidence}

Analyze every major factual claim in the answer.

Classify each claim as:

SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED

Return:

OVERALL VERDICT:
PASS / REVIEW_REQUIRED

CLAIMS:

1. Claim:
   Status:
   Evidence:

2. Claim:
   Status:
   Evidence:

Do not use outside knowledge.
Only compare the answer with the supplied evidence.
"""

    response = get_llm().invoke(prompt)

    return response.content