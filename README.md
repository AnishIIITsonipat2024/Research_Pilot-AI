# ResearchPilot AI

ResearchPilot AI is a Streamlit research assistant backed by a supervisor-routed
LangGraph workflow. It searches Crossref and arXiv, retrieves locally indexed PDF
evidence, analyzes and cites the sources, and asks a critic to approve or request
bounded revisions before writing the final report.

## Requirements

- Python 3.10 or newer
- A Groq API key

## Install

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set `GROQ_API_KEY` in the environment or in a local `.env` file in the project
directory. The application can start without the key, but a research run requires
it. `GROQ_MODEL` optionally overrides the default Groq model
(`openai/gpt-oss-120b`). Do not commit API keys.

LangSmith tracing is optional. Configure the standard LangChain variables
(`LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, and `LANGSMITH_PROJECT`) to enable it.
The project does not require an OpenAI API key.

## Run

Start the Streamlit interface from the project directory:

```powershell
streamlit run frontend/streamlit_app.py
```

Or run the command-line interface:

```powershell
python -m backend.main
```

Run the local test suite with:

```powershell
python -m unittest discover -s tests -v
```

## Local research documents

Upload a PDF in the Streamlit app and select **Index PDF** to split and store its
text in Chroma at `chroma_db`. Set `CHROMA_PERSIST_DIRECTORY` to use another
location. The repository does not include an indexed document collection; local
PDF retrieval is optional because the research agent also searches Crossref and
arXiv.

The supervisor routes through missing research stages based on state, then runs
the critic. If the critic requests changes, the supervisor chooses a revision
specialist and loops through analysis, citations, and review again, up to two
revision rounds. If the limit is reached, the report is labeled as not approved
and includes the outstanding review issues.