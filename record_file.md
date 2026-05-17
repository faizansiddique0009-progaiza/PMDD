# Project Record File: Pragmatic Meaning Drift Detector (PMDD)

## 📌 Project Overview
**What is it?** 
The PMDD is an AI-powered application that uses a team of 5 specialized "Agents" to read large amounts of text (like speeches or news articles) and figure out how the true meaning, tone, and context of words change over time.
**Platform:** Google Antigravity IDE
**Tools:** Python, Multi-Agent Framework, OpenAI GPT-4o
**Memory System:** Episodic Memory (A "Team Journal" so the AI never makes the same mistake twice).

## 🟢 What is Done (Completed)
- [x] Read and analyzed the core project documentation (`project_description.txt`).
- [x] Translated complex linguistic theories into plain, non-technical English.
- [x] Defined the roles of the 5 Agents (The Organizer, The Intent Reader, The Topic Tracker, The Number Cruncher, The Big Boss).
- [x] Established the memory learning system so agents learn from past responses.
- [x] Created this continuous Record File for hand-overs and tracking.

## 🟡 What is Doing (In Progress)
- [ ] End-to-End Testing: Running the newly rewritten 5-agent pipeline on a test corpus.

## 🔴 What Needs to be Done (To-Do / Next Steps)
Here is our roadmap to build this project together, step-by-step:

### Phase 1: Setup & Foundations
- [x] Ensure Python is installed and ready.
- [x] Install required tools (`openai`, `spacy`, `nltk`, `pandas`, `gradio`, `pymupdf`).
- [x] Set up the folder structure (`agents/`, `utils/`, `outputs/`).

### Phase 2: Building the Team (The Agents)
- [x] **Agent 1 (Preprocessor):** Fully rewritten. Parses TXT, CSV, JSON, PDF (via PyMuPDF). Segments by 3 sentences using spaCy.
- [x] **Agent 2 (Pragmatic):** Rewritten with exact `AGENT2_SYSTEM_PROMPT` for Speech Act Theory, Gricean Maxims, Politeness. API Key integrated.
- [x] **Agent 3 (Semantic):** Rewritten with exact `AGENT3_SYSTEM_PROMPT` for Semantic Field and Register Analysis. API Key integrated.
- [x] **Agent 4 (Statistics):** Refactored to pure Python/NLTK. Computes Frequency, TTR, Collocations, MI Score, and Keyness without GPT calls.
- [x] **Agent 5 (Orchestrator):** Rewritten with exact `AGENT5_SYSTEM_PROMPT` to synthesize report, check quality, and compute 40/30/20/10 Drift Score.

### Phase 3: The User Interface & Testing
- [x] **UI Application:** Updated Gradio `app.py` blocks to match the specified UI (added Landing page, file upload, text pasting, and live agent progress updates).
- [ ] **End-to-End Pipeline Testing:** Validate that all 5 agents execute sequentially without failing on a real set of documents.
- [ ] **JSON & Markdown Export:** Validate that the output report generates clean Markdown and Evidence is exported to JSON successfully in `outputs/reports/`.

---

## 📜 Complete Project History & Changelog

### Step 1: Initial Setup & Understanding
- **Action:** Read the core project documentation (`project_description.txt`, `agentic_ai_linguistics_lecture (1).docx`, `PMDD_Complete_StepByStep_Guide.docx`).
- **Result:** Defined the architecture of the 5-Agent PMDD system and translated complex linguistic theories into a plain, non-technical understanding.
- **Action:** Set up the project directory (`d:\pmdd`), initialized `requirements.txt`, and installed all necessary Python dependencies (`openai`, `spacy`, `nltk`, `pandas`, `gradio`, `pymupdf`).

### Step 2: Building the Agents (Backend Logic)
- **Action:** Created the `utils/helpers.py` file to handle JSON parsing, progress formatting, and file generation.
- **Action:** Built **Agent 1 (Preprocessor)** to read and segment raw text, PDF, CSV, and JSON files into 3-sentence chunks using `spaCy`.
- **Action:** Built **Agent 2 (Pragmatic)** and integrated the OpenAI API with strict prompts for Speech Act Theory, Gricean Maxims, and Politeness.
- **Action:** Built **Agent 3 (Semantic)** and integrated OpenAI API to detect semantic field shifts and register analysis.
- **Action:** Built **Agent 4 (Statistics)** using Python and NLTK to handle math-intensive linguistic metrics (Frequency, Type-Token Ratio, Collocations, MI Score, Keyness).
- **Action:** Built **Agent 5 (Orchestrator)** to evaluate the outputs of Agents 1-4, trigger quality checks, calculate the final weighted Drift Score, and generate academic Markdown and JSON reports.

### Step 3: Gradio Interface Implementation
- **Action:** Developed the `app.py` file with a Gradio web interface.
- **Action:** Refined the UI to serve as a user-friendly Landing Page. Added clear "Input Options" allowing users to either **upload a file** or **paste text directly**. Added progress-logging text boxes for live status updates from the agents.
- **Action:** Updated Agent 1 to gracefully accept raw pasted text directly from the UI without needing a file object.

### Step 4: UI Refactoring & Feedback Loops
- **Action:** Refactored `app.py` from a sequential generator pipeline into a stateful, interactive Gradio application using `gr.State`.
- **Action:** Implemented "Agent Cards" (Accordions) for each of the five analysis agents.
- **Action:** Updated backend Agents (2, 3, and 4) to accept user feedback strings and dynamically inject them into the GPT-4o system prompts.
- **Action:** Added interactive Textboxes, Rating buttons, and "Re-run" logic to Agents 2, 3, and 4 to allow downstream refinement of the analysis based on human feedback.

### Step 5: Next.js Dashboard Migration & Deployment
- **Action:** Migrated the frontend to a modern, single-page Next.js dashboard application with TailwindCSS.
- **Action:** Rebuilt the 5 agents as sequential Next.js API routes (`/api/analyze`).
- **Action:** Added data visualization (Radar Charts) to the Final Report using `recharts`.
- **Status:** The application is fully functional locally on port 3000 and deployed to Firebase Hosting. Interactive feedback loops, streaming updates, and charting are actively working.
