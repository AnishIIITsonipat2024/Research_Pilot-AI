import unittest
from unittest.mock import patch

from backend.agents.supervisor import supervisor, supervisor_router
from backend.graph import workflow as workflow_module
from backend.graph.workflow import create_workflow


class SupervisorTests(unittest.TestCase):
    def test_routes_initial_workflow_stages(self):
        state = {}
        expected_agents = (
            "research",
            "rag",
            "analysis",
            "citation",
            "critic",
            "writer",
            "end",
        )

        for agent in expected_agents:
            state.update(supervisor(state))
            self.assertEqual(supervisor_router(state), agent)
            if agent == "research":
                state["research_plan"] = "plan"
            elif agent == "rag":
                state["retrieved_context"] = "evidence"
            elif agent == "analysis":
                state["analysis"] = "analysis"
            elif agent == "citation":
                state["citations"] = []
            elif agent == "critic":
                state.update({"critique": "PASS", "revision_required": False})
            elif agent == "writer":
                state["final_report"] = "report"

    def test_routes_revisions_to_critic_selected_specialist(self):
        state = {
            "critique": "REVISION_REQUIRED",
            "revision_required": True,
            "revision_target": "rag",
            "iteration": 1,
            "max_iterations": 2,
        }
        expected_agents = ("rag", "analysis", "citation", "critic")

        for agent in expected_agents:
            update = supervisor(state)
            self.assertEqual(update["next_agent"], agent)
            state.update(update)

    def test_allows_maximum_revision_rounds_then_stops(self):
        last_allowed_round = supervisor(
            {
                "critique": "REVISION_REQUIRED",
                "revision_required": True,
                "iteration": 2,
                "max_iterations": 2,
            }
        )
        self.assertEqual(last_allowed_round["next_agent"], "analysis")

        result = supervisor(
            {
                "critique": "REVISION_REQUIRED",
                "revision_required": True,
                "iteration": 3,
                "max_iterations": 2,
            }
        )
        self.assertEqual(result["next_agent"], "writer")
        self.assertEqual(result["workflow_status"], "max_iterations_reached")

    def test_prioritizes_or_skips_local_retrieval_from_state(self):
        prioritized = supervisor(
            {
                "prioritize_local_documents": True,
                "use_local_documents": True,
            }
        )
        self.assertEqual(prioritized["next_agent"], "rag")

        skipped = supervisor(
            {
                "research_plan": "plan",
                "use_local_documents": False,
            }
        )
        self.assertEqual(skipped["next_agent"], "analysis")
        self.assertEqual(skipped["retrieved_sources"], [])

    def test_rejects_unknown_route(self):
        with self.assertRaises(ValueError):
            supervisor_router({"next_agent": "unknown"})

    def test_workflow_compiles_with_supervisor_cycles(self):
        graph = create_workflow().get_graph()
        self.assertTrue({"supervisor", "research", "rag", "analysis", "citation", "critic", "writer"} <= set(graph.nodes))

    def test_compiled_graph_revisits_specialists_before_writing(self):
        critic = patch.object(
            workflow_module,
            "critic_agent",
            side_effect=[
                {
                    "critique": "REVISION_REQUIRED",
                    "revision_required": True,
                    "revision_target": "citation",
                    "revision_step": 0,
                    "iteration": 1,
                    "issues": ["Citation needs correction"],
                },
                {
                    "critique": "PASS",
                    "revision_required": False,
                    "revision_step": 0,
                    "iteration": 1,
                    "issues": [],
                },
            ],
        )
        research = patch.object(
            workflow_module,
            "research_agent",
            return_value={
                "research_plan": "Plan",
                "research_results": ["Evidence"],
                "sources": [{"title": "Paper", "abstract": "Evidence", "source_id": "P1"}],
            },
        )
        rag = patch.object(
            workflow_module,
            "rag_agent",
            return_value={
                "retrieved_context": "Local evidence",
                "retrieved_documents": ["Local evidence"],
                "retrieved_sources": [],
            },
        )
        analysis = patch.object(
            workflow_module,
            "analysis_agent",
            return_value={"analysis": "Analysis"},
        )
        citation = patch.object(
            workflow_module,
            "citation_agent",
            return_value={"citations": ["[P1] Paper"], "citation_map": {}},
        )
        writer = patch.object(
            workflow_module,
            "writer_agent",
            return_value={"final_report": "Final report", "workflow_status": "completed"},
        )

        with (
            critic as critic_agent,
            research,
            rag,
            analysis as analysis_agent,
            citation as citation_agent,
            writer as writer_agent,
        ):
            result = create_workflow().invoke(
                {"query": "Question", "max_iterations": 2}
            )

        self.assertEqual(result["final_report"], "Final report")
        self.assertEqual(result["workflow_status"], "completed")
        self.assertEqual(analysis_agent.call_count, 2)
        self.assertEqual(citation_agent.call_count, 3)
        self.assertEqual(critic_agent.call_count, 2)
        writer_agent.assert_called_once()


if __name__ == "__main__":
    unittest.main()
