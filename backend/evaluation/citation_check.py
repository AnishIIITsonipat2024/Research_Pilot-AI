from backend.config import get_llm


def check_citation(claim: str, evidence: str):
    """
    Check whether the supplied evidence supports a claim.

    Returns:
        A structured verification result.
    """

    prompt = f"""
You are a strict academic citation verification agent.

CLAIM:
{claim}

EVIDENCE:
{evidence}

Determine whether the evidence actually supports the claim.

Return exactly this structure:

VERDICT: SUPPORTED / PARTIALLY_SUPPORTED / UNSUPPORTED

REASON:
Explain why.

EVIDENCE:
Quote or identify the relevant evidence.

Do not use outside knowledge.
Do not invent information.
"""

    response = get_llm().invoke(prompt)

    return response.content


def verify_claims(claims: list[str], evidence: str) -> list[dict[str, str]]:
    """
    Verify multiple claims against the supplied evidence.
    """

    results = []

    for claim in claims:

        result = check_citation(
            claim,
            evidence
        )

        results.append({
            "claim": claim,
            "verification": result
        })

    return results