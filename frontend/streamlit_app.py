from pathlib import Path

import streamlit as st

from backend.config import VECTORSTORE_PATH
from backend.rag.ingest import index_pdf
from backend.graph.workflow import create_workflow


st.set_page_config(
    page_title="ResearchPilot AI",
    page_icon="🔬",
    layout="wide"
)


st.title("🔬 ResearchPilot AI")

st.subheader(
    "Autonomous Research Assistant"
)

st.markdown(
    "Searches Crossref and arXiv, retrieves indexed PDFs, and uses an iterative "
    "LangGraph review loop to produce a cited report."
)

uploaded_pdf = st.file_uploader("Add a research PDF to the local library", type=["pdf"])
if st.button("Index PDF", disabled=uploaded_pdf is None):
    if uploaded_pdf is None:
        st.warning("Choose a PDF before indexing.")
    else:
        chunk_count = index_pdf(uploaded_pdf.name, uploaded_pdf.getvalue())
        st.success(f"Indexed {chunk_count} text chunks from {uploaded_pdf.name}.")

use_local_documents = st.checkbox(
    "Include indexed PDFs",
    value=Path(VECTORSTORE_PATH).exists(),
)
prioritize_local_documents = st.checkbox(
    "Search indexed PDFs before external papers",
    value=False,
    disabled=not use_local_documents,
)

query = st.text_area(
    "Enter your research question",
    placeholder="What does recent research say about ...?",
)


if st.button("🚀 Start Research"):

    if not query.strip():

        st.warning(
            "Please enter a research question."
        )

    else:

        with st.spinner(
            "ResearchPilot is researching..."
        ):
            app = create_workflow()
            result = app.invoke({
                "query": query,
                "max_iterations": 2,
                "use_local_documents": use_local_documents,
                "prioritize_local_documents": prioritize_local_documents,
            })

        if result.get("workflow_status") == "max_iterations_reached":
            st.warning("Research completed with unresolved critic feedback.")
        else:
            st.success("Research completed and reviewed.")

        st.markdown(
            result.get(
                "final_report",
                "No report generated."
            )
        )

        if result.get("errors"):
            st.warning("Some research sources could not be reached:")
            for error in result["errors"]:
                st.write(f"- {error}")

        citation_map = result.get("citation_map", {})
        if citation_map:
            with st.expander("Sources and citations"):
                for citation in result.get("citations", []):
                    st.write(citation)