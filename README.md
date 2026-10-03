# 🔬 ResearchPilot AI — Autonomous Multi-Agent Research Assistant

**ResearchPilot AI** is an autonomous research assistant built with **LangGraph, LangChain, Groq, RAG, ChromaDB, Crossref, arXiv, and Streamlit**.

It automates a complete research workflow: understanding a research question, searching academic sources, retrieving evidence from uploaded PDFs, analyzing information, generating citations, reviewing the answer through a critic agent, performing bounded revisions, and producing a structured final research report.

## 🚀 Live Demo

🌐 **Try ResearchPilot AI:**
https://researchpilot-aigit-yqrkrvctgobxsfugevgbvn.streamlit.app/

> The application is deployed using Streamlit Community Cloud.

---

# 🎯 What Problem Does It Solve?

Research often requires switching between multiple tools:

* 🔎 Search for research papers
* 📄 Read and analyze PDFs
* 🧠 Understand and compare findings
* 🔗 Track sources and citations
* ✍️ Write a structured report
* 🔍 Check whether claims are actually supported
* 🔄 Revise the report when problems are found

ResearchPilot AI combines these tasks into a single **multi-agent research workflow**.

Instead of simply asking an LLM:

```text
Question → LLM → Answer
```

ResearchPilot AI uses:

```text
Research Question
       ↓
   Supervisor
       ↓
 ┌─────┼─────────┐
 ↓     ↓         ↓
Research  RAG   Analysis
 Agent    Agent   Agent
 ↓         ↓       ↓
 └──────→ Citation
              ↓
            Critic
              ↓
        ┌─────┴─────┐
        ↓           ↓
    Revision      Approved
        ↓           ↓
   Supervisor      Writer
        ↓           ↓
      Critic ←──────┘
                    ↓
              Final Report
```

---

# 🧠 Core Workflow

## 1. User Research Query

The user enters a research question such as:

```text
What are the recent approaches for detecting deepfakes using
vision transformers?
```

The query becomes the initial state of the LangGraph workflow.

---

## 2. Supervisor Agent

The **Supervisor Agent** manages the research workflow.

It determines which research stages are still required and routes the state to the appropriate agent.

```text
                    Supervisor
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    Research           RAG           Analysis
        │               │               │
        └───────────────┼───────────────┘
                        ↓
                    Citation
                        ↓
                     Critic
```

The supervisor is state-driven rather than simply executing every agent blindly.

---

# 🔎 3. Research Agent

The Research Agent searches academic sources including:

* Crossref
* arXiv

It collects relevant research information that can be used by downstream agents.

Example:

```text
Research Question
      ↓
Crossref / arXiv
      ↓
Relevant Papers
      ↓
Research Evidence
```

---

# 📚 4. PDF RAG Agent

Users can upload their own research papers or documents.

The PDF pipeline is:

```text
PDF
 ↓
PDF Loader
 ↓
Text Extraction
 ↓
Recursive Text Splitting
 ↓
Embeddings
 ↓
ChromaDB
 ↓
Retriever
 ↓
Relevant Chunks
 ↓
Research Workflow
```

This allows ResearchPilot AI to answer questions using evidence from the user's own documents.

### Local Vector Store

The project uses **ChromaDB** for local vector storage.

By default:

```text
chroma_db/
```

is used as the persistence directory.

The location can be changed with:

```text
CHROMA_PERSIST_DIRECTORY
```

---

# 🧠 5. Analysis Agent

The Analysis Agent receives research evidence and retrieved PDF information.

It can:

* summarize findings
* compare approaches
* identify important observations
* synthesize information from multiple sources
* generate key findings

Example:

```text
Paper A ──┐
Paper B ──┼──→ Analysis Agent → Key Findings
Paper C ──┘
PDF Data ──┘
```

---

# 🔗 6. Citation Agent

The Citation Agent connects research claims with their supporting sources.

The goal is to reduce unsupported statements and make the final report easier to verify.

```text
Claim
 ↓
Supporting Evidence
 ↓
Source
 ↓
Citation
```

The system maintains citation/source information as part of the research state.

---

# 🧐 7. Critic Agent

ResearchPilot AI does not immediately accept the generated analysis.

The Critic Agent reviews the research output and checks for issues such as:

* unsupported claims
* insufficient evidence
* citation problems
* missing information
* research-quality issues

The critic can return:

```text
APPROVED
```

or:

```text
REVISION REQUIRED
```

---

# 🔄 8. Bounded Revision Loop

If the critic finds problems, the workflow does not restart indefinitely.

The supervisor routes the state back to the appropriate specialist.

```text
Critic
  │
  ├── Approved ─────────→ Writer
  │
  └── Revision Required
              ↓
          Supervisor
              ↓
       Analysis / Citation
              ↓
            Critic
```

The current implementation limits revision rounds to **two iterations**.

This prevents uncontrolled agent loops and unnecessary API calls.

If the revision limit is reached, the report is clearly marked as not approved and includes the outstanding review issues.

---

# ✍️ 9. Writer Agent

Once the research passes the review stage, the Writer Agent generates the final structured research report.

The final output can contain:

* Research overview
* Key findings
* Analysis
* Comparisons
* Supporting evidence
* Citations
* Critic/review information
* Outstanding issues when applicable

---

# 🏗️ System Architecture

```text
```
