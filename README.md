# Confidential AI Data Analysis

A Streamlit app that runs automated data analysis using AI agents. Data stays on your machine: only metadata (schema, types, relationships) is sent to the LLM agents. Raw data never leaves your environment.

---

## Prerequisites

- **Python 3.10+**
- **OpenAI API key** (used by the agents)

---

## Quick start (une seule commande)

Clone du repo, création de l’environnement virtuel, installation des dépendances et lancement de l’app en une commande.

**Linux / macOS :**

```bash
git clone git@github.com:Ziwo99/data_analysis.git && cd data_analysis && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python run_app.py
```

**Windows (CMD ou PowerShell) :**

```bash
git clone git@github.com:Ziwo99/data_analysis.git && cd data_analysis && python -m venv .venv && .venv\Scripts\activate.bat && pip install -r requirements.txt && python run_app.py
```

L’app s’ouvre dans le navigateur (http://localhost:8501).

---

## Installation (étape par étape)

1. Clone or download this repository.
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   # or:  .venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Dependencies: `streamlit`, `streamlit-autorefresh`, `pandas`, `openpyxl`, `crewai`, `openai`, `pydantic`, `matplotlib`, `seaborn`.

---

## How to run

From the **project root** (the folder containing `run_app.py`):

```bash
python run_app.py
```

The app opens in your browser (Streamlit default: http://localhost:8501).

---

## How to use

### Landing page: two options

1. **New Analysis** — Start a new run on your data or test_data.
2. **Load Analysis** — Open a previously saved analysis.

---

### New analysis (step by step)

1. **Choose pipeline mode** (in **Settings** ⚙️ on the landing page):
   - **Multi-Agent**: several specialized agents in sequence (schema → business → queries → visualizations → confidentiality). More detailed, more steps.
   - **Mono-Agent**: one agent does the full pipeline in a single pass. Faster, one LLM call.

2. **Configure LLM Settings** (in **Settings** ⚙️ on the landing page):
   - **OpenAI API Key**: required. Used for all agents.
   - **OpenAI Model**: e.g. `gpt-4o`, `gpt-4o-mini`, etc.

3. **Choose data source** (one of the two):
   - **Upload a dataset**: drag & drop one or more **CSV or Excel** files.
   - **Use an existing dataset**: pick a dataset from `test_data/` (e.g. `1-students`, `2-ecommerce`, `6-supermarket`).

4. **Validate dataset**: Click **Validate dataset** after selecting files or a folder. You can then preview tables and see which metadata is shared with the agents.

5. **Analysis name**: Enter a unique name (e.g. `Sales Q4 2024`). It is used to save and find the analysis later.

6. **Launch**: Click **Launch Analysis**. The pipeline runs; you can follow progress on the analysis page. When it finishes, the analysis is saved automatically.

---

### Load a saved analysis

- Select **Load Analysis** on the landing page.
- Choose an analysis from the list (dataset, date, pipeline mode and model are shown).
- Click **Load Analysis** to open it, or **Delete** to remove it (with confirmation).

---

### Analysis page (after launch or load)

- **Navigation**: Use the section buttons to move between steps: Raw schema → Schema → Business → Query analysis → Visualization → Confidentiality. You can also open the **Report** view, the **Performance** view or **Download** source data used for the analysis.
- **Sections content**: Each section shows the outputs of the corresponding step (tables, business grid, queries, charts, confidentiality test).
- **Report view**: A single-page report of the analysis: analyses and sub-analyses with context, tables used, objectives, expected results, and all visualizations.
- **Performance view**: Execution summary for the run: a table of each step of the analysis pipeline with execution time, number of attempts and status.
- **Errors**: If there is an API error, you are sent back to the landing page with a message; you can fix Settings and try again.

---

## Project structure (brief)

| Path | Role |
|------|------|
| `run_app.py` | Entry point: launches the Streamlit app. |
| `src/data_analysis/` | Main application package (UI, crew, system). |
| `src/data_analysis/crew/` | Agents, tasks, CrewAI config (YAML) and Pydantic models (schema, business, queries, visualizations, confidentiality). |
| `src/data_analysis/system/` | Guardrails, scripts (metadata extractor, queries analyser) and utils (paths, saved analyses, code execution, etc.). |
| `analyses/` | Run outputs: `current_analysis/` (active run), `saved_analyses/<name>/` (one folder per saved analysis). |
| `test_data/` | Sample datasets (CSV) you can choose in “Use an existing dataset”. Add your own folders here if you want to have them listed. |

Agent prompts (role, goal, backstory, task instructions) are defined in the YAML files under `src/data_analysis/crew/config/` (`agents.yaml`, `mono_agents.yaml`, `tasks.yaml`, `mono_tasks.yaml`).

---
