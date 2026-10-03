from langgraph.graph import StateGraph, START, END

from backend.graph.state import ResearchState

from backend.agents.supervisor import supervisor, supervisor_router
from backend.agents.research_agent import research_agent
from backend.agents.rag_agent import rag_agent
from backend.agents.analysis_agent import analysis_agent
from backend.agents.citation_agent import citation_agent
from backend.agents.critic_agent import critic_agent
from backend.agents.writer_agent import writer_agent


def create_workflow():

    workflow = StateGraph(ResearchState)

    # Nodes
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("research", research_agent)
    workflow.add_node("rag", rag_agent)
    workflow.add_node("analysis", analysis_agent)
    workflow.add_node("citation", citation_agent)
    workflow.add_node("critic", critic_agent)
    workflow.add_node("writer", writer_agent)

    # Start
    workflow.add_edge(START, "supervisor")

    # Supervisor decides where to go
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "research": "research",
            "rag": "rag",
            "analysis": "analysis",
            "citation": "citation",
            "critic": "critic",
            "writer": "writer",
            "end": END,
        }
    )

    # Agents return to supervisor
    workflow.add_edge("research", "supervisor")
    workflow.add_edge("rag", "supervisor")
    workflow.add_edge("analysis", "supervisor")
    workflow.add_edge("citation", "supervisor")

    # Critic also returns to supervisor
    workflow.add_edge("critic", "supervisor")

    # Writer finishes
    workflow.add_edge("writer", END)

    return workflow.compile()