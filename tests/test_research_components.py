import io
import unittest
from unittest.mock import Mock, patch

from langchain_core.documents import Document

from backend.agents.citation_agent import citation_agent
from backend.agents.critic_agent import critic_agent
from backend.agents.rag_agent import rag_agent
from backend.agents.research_agent import research_agent
from backend.rag.ingest import index_pdf
from backend.tools.paper_search import search_papers
from backend.tools.web_search import search_arxiv


class ResearchComponentTests(unittest.TestCase):
    def test_crossref_search_normalizes_citation_metadata(self):
        response = io.BytesIO(
            b'{"message":{"items":[{"title":["A study"],"author":[{"given":"Ada","family":"Lovelace"}],'
            b'"published-print":{"date-parts":[[2024,2]]},"abstract":"<jats:p>Evidence</jats:p>",'
            b'"DOI":"10.1/example","URL":"https://doi.org/10.1/example"}]}}'
        )
        with patch("backend.tools.paper_search.urlopen", return_value=response):
            papers = search_papers("research question")

        self.assertEqual(papers[0]["title"], "A study")
        self.assertEqual(papers[0]["authors"], ["Ada Lovelace"])
        self.assertEqual(papers[0]["published"], "2024-2")
        self.assertEqual(papers[0]["abstract"], "Evidence")

    def test_arxiv_search_reads_atom_results(self):
        feed = b"""<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><id>https://arxiv.org/abs/1234.5678</id><title>A paper</title>
          <summary> Abstract text </summary><published>2025-01-02T00:00:00Z</published>
          <author><name>Grace Hopper</name></author></entry>
        </feed>"""
        with patch(
            "backend.tools.web_search.urlopen", return_value=io.BytesIO(feed)
        ):
            papers = search_arxiv("research question")

        self.assertEqual(papers[0]["title"], "A paper")
        self.assertEqual(papers[0]["authors"], ["Grace Hopper"])
        self.assertEqual(papers[0]["published"], "2025-01-02")

    def test_research_agent_records_sources_and_search_errors(self):
        llm = Mock()
        llm.invoke.return_value.content = (
            "Research plan\n4. SEARCH QUERIES\n- follow-up question\n5. Other"
        )
        with (
            patch(
                "backend.agents.research_agent.search_papers",
                side_effect=[
                    [
                        {
                            "title": "Paper",
                            "authors": ["A. Author"],
                            "abstract": "Evidence",
                            "doi": "10.1/one",
                            "url": "https://doi.org/10.1/one",
                        }
                    ],
                    [
                        {
                            "title": "Second paper",
                            "authors": [],
                            "abstract": "More evidence",
                            "doi": "10.1/two",
                            "url": "https://doi.org/10.1/two",
                        }
                    ],
                ],
            ),
            patch(
                "backend.agents.research_agent.search_arxiv",
                side_effect=RuntimeError("arXiv unavailable"),
            ),
            patch("backend.agents.research_agent.get_llm", return_value=llm),
        ):
            result = research_agent({"query": "A research question"})

        self.assertIn("Research plan", result["research_plan"])
        self.assertEqual(result["sources"][0]["source_id"], "P1")
        self.assertEqual(result["sources"][1]["source_id"], "P2")
        self.assertEqual(
            result["search_queries"],
            ["A research question", "follow-up question"],
        )
        self.assertIn("arXiv unavailable", result["errors"][0])

    def test_rag_agent_returns_documents_and_empty_library_context(self):
        retriever = Mock()
        retriever.invoke.return_value = [
            Document(page_content="Local evidence", metadata={"source": "paper.pdf", "page": 0})
        ]
        with patch("backend.agents.rag_agent.get_retriever", return_value=retriever):
            result = rag_agent({"query": "question"})

        self.assertEqual(result["retrieved_documents"], ["Local evidence"])
        self.assertEqual(result["retrieved_sources"][0]["source_id"], "R1")

        retriever.invoke.return_value = []
        with patch("backend.agents.rag_agent.get_retriever", return_value=retriever):
            empty_result = rag_agent({"query": "question"})
        self.assertIn("No matching local documents", empty_result["retrieved_context"])

    def test_citation_agent_builds_references_from_both_source_types(self):
        result = citation_agent(
            {
                "sources": [
                    {
                        "source_id": "P1",
                        "title": "Published paper",
                        "authors": ["A. Author"],
                        "published": "2024",
                        "url": "https://doi.org/1",
                    }
                ],
                "retrieved_sources": [
                    {"source_id": "R1", "source": "local.pdf", "page": 0}
                ],
            }
        )

        self.assertEqual(set(result["citation_map"]), {"P1", "R1"})
        self.assertTrue(any("p. 1" in citation for citation in result["citations"]))

    def test_critic_fails_closed_without_source_evidence(self):
        llm = Mock()
        llm.invoke.return_value.content = (
            "VERDICT: PASS\nISSUES: None\nNEXT_AGENT: analysis\n"
        )
        with patch("backend.agents.critic_agent.get_llm", return_value=llm):
            result = critic_agent(
                {
                    "analysis": "Unsupported",
                    "sources": [{"abstract": ""}],
                    "retrieved_documents": [],
                    "iteration": 0,
                }
            )

        self.assertTrue(result["revision_required"])
        self.assertEqual(result["iteration"], 1)
        self.assertIn(
            "No supporting source text or research-paper abstracts were available.",
            result["issues"],
        )

    def test_pdf_ingestion_validates_and_forwards_uploaded_file(self):
        with self.assertRaises(ValueError):
            index_pdf("notes.txt", b"text")
        with self.assertRaises(ValueError):
            index_pdf("paper.pdf", b"")

        with patch("backend.rag.ingest.index_pdf_file", return_value=1) as index_file:
            chunk_count = index_pdf("paper.pdf", b"pdf bytes")

        self.assertEqual(chunk_count, 1)
        self.assertEqual(index_file.call_args.kwargs["source_name"], "paper.pdf")

    def test_pdf_tool_extracts_chunks_and_sets_source_name(self):
        from backend.tools.pdf_tool import index_pdf_file

        document = Document(page_content="paper text", metadata={"page": 0})
        with (
            patch("backend.tools.pdf_tool.load_pdf", return_value=[document]),
            patch("backend.tools.pdf_tool.create_vectorstore") as create_vectorstore,
        ):
            chunk_count = index_pdf_file("upload.pdf", source_name="paper.pdf")

        self.assertEqual(chunk_count, 1)
        self.assertEqual(document.metadata["source"], "paper.pdf")
        create_vectorstore.assert_called_once()


if __name__ == "__main__":
    unittest.main()
