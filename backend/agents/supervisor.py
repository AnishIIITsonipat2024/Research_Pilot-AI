from backend.graph.state import ResearchState


VALID_AGENTS = {"research", "rag", "analysis", "citation", "critic", "writer", "end"}


def supervisor(state: ResearchState) -> ResearchState:
    iteration = max(0, int(state.get("iteration", 0)))
    max_iterations = max(0, int(state.get("max_iterations", 2)))

    if "final_report" in state:
        return {
            "next_agent": "end",
            "current_agent": "supervisor",
            "workflow_status": state.get("workflow_status", "completed"),
        }

    if "critique" in state:
        if not state.get("revision_required", False):
            return {
                "next_agent": "writer",
                "workflow_status": "approved",
                "current_agent": "writer",
            }

        if iteration > max_iterations:
            return {
                "next_agent": "writer",
                "workflow_status": "max_iterations_reached",
                "current_agent": "writer",
            }

        revision_step = int(state.get("revision_step", 0))
        revision_target = state.get("revision_target", "analysis")
        if revision_step == 0:
            next_agent = revision_target
        elif revision_step == 1:
            next_agent = "analysis"
        elif revision_step == 2:
            next_agent = "citation"
        elif revision_step == 3:
            next_agent = "critic"
        else:
            raise ValueError(f"Invalid revision step: {revision_step}")

        if next_agent not in VALID_AGENTS - {"writer", "end"}:
            raise ValueError(f"Supervisor selected an invalid revision agent: {next_agent!r}")

        return {
            "next_agent": next_agent,
            "current_agent": next_agent,
            "revision_step": revision_step + 1,
            "workflow_status": "revising",
        }

    use_local_documents = state.get("use_local_documents", True)
    prioritize_local_documents = state.get("prioritize_local_documents", False)

    if (
        use_local_documents
        and prioritize_local_documents
        and "retrieved_context" not in state
    ):
        next_agent = "rag"
    elif "research_plan" not in state:
        next_agent = "research"
    elif "retrieved_context" not in state:
        if use_local_documents:
            next_agent = "rag"
        else:
            return {
                "next_agent": "analysis",
                "current_agent": "analysis",
                "retrieved_context": "Local document retrieval was disabled.",
                "retrieved_documents": [],
                "retrieved_sources": [],
                "workflow_status": state.get("workflow_status", "running"),
            }
    elif "analysis" not in state:
        next_agent = "analysis"
    elif "citations" not in state:
        next_agent = "citation"
    elif "critique" not in state:
        next_agent = "critic"
    else:
        next_agent = "end"

    return {
        "next_agent": next_agent,
        "current_agent": next_agent,
        "iteration": iteration,
        "max_iterations": max_iterations,
        "workflow_status": state.get("workflow_status", "running"),
    }


def supervisor_router(state: ResearchState) -> str:
    next_agent = state.get("next_agent")

    if next_agent not in VALID_AGENTS:
        raise ValueError(f"Supervisor selected an invalid agent: {next_agent!r}")

    return next_agent