# Power-BI-chatbot

**Power BI + Ollama + RAG + read-only SQL + ChatGPT-style interface**

GitHub repository: https://github.com/vinay-kumar0901/Power-BI-chatbot

This project provides a local BI assistant that can inspect Power BI Project (PBIP) metadata, retrieve relevant model information with RAG, use Ollama for natural-language answers and SQL proposals, execute validated read-only SQL against imported CSV/Excel data in SQLite, and preserve local chat history.

> **Important:** This is a local development project, not a production multi-user service. Do not expose it publicly or upload confidential business data without authentication, authorization, and appropriate data controls.

## Repository contents

- `app/` — FastAPI backend, chat UI, RAG, Ollama integration, PBIP inspection, SQLite data import and read-only SQL agent.
- `powerbi/` — included sample Power BI project.
- `data/` — included sample workbook / data files.
- `knowledge/` — glossary, schema and metric notes.
- `run_setup.py` — initializes the local storage and imports available data.
- `requirements.txt` — Python dependencies.
- `BI_GPT_Advanced_Colab.ipynb` — Google Colab launch notebook (if included in the repository root by you).

## 1. Download from GitHub

Open the repository:

https://github.com/vinay-kumar0901/Power-BI-chatbot

Select **Code → Download ZIP**, then extract the downloaded repository archive.

GitHub normally names its downloaded archive after the repository and branch, for example `Power-BI-chatbot-main.zip`. This project package is also provided separately as `Power-BI-chatbot.zip`.

## 2. Run locally on Windows

### Requirements

1. Windows 10/11, 64-bit.
2. Python 3.11 or 3.12 (recommended).
3. Ollama for Windows: https://ollama.com/download
4. At least several GB of free disk space for the model and Python packages.

### Steps

Open PowerShell in the extracted project folder — the folder that contains `requirements.txt` and `run_setup.py`.

```powershell
# Optional: verify Python
py --version

# Create and activate a virtual environment
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create local environment configuration
Copy-Item .env.example .env

# Download the Ollama model used by default
ollama pull llama3.2:1b

# Initialize storage and import included data
python run_setup.py

# Start the web application
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If PowerShell blocks environment activation, run this once in the same PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open the application:

- Chat interface: http://127.0.0.1:8000
- API health: http://127.0.0.1:8000/api/health
- API documentation: http://127.0.0.1:8000/docs

**Ollama must be running** in the background. If it is not, start the Ollama desktop app or run `ollama serve` in a separate terminal. Do not start a second server if the Ollama desktop service is already running.

### Stop the application

Press `Ctrl+C` in the terminal running Uvicorn. The virtual environment can be deactivated with:

```powershell
deactivate
```

## 3. Run in Google Colab

Use the provided notebook `Power-BI-chatbot_Colab.ipynb` (or upload the notebook committed to this repository).

1. Open https://colab.research.google.com/.
2. Choose **File → Upload notebook** and upload the Colab `.ipynb` file.
3. In the notebook, choose **Runtime → Change runtime type**. A GPU runtime can help if one is available, but the notebook is configured to use the `llama3.2:1b` model.
4. Run the notebook cells from top to bottom.
5. When the upload cell appears, upload `Power-BI-chatbot.zip` (or the ZIP downloaded from this GitHub repository).
6. Wait for dependencies, Ollama, and the model to install/download.
7. Wait for the notebook to verify the FastAPI app and Cloudflare tunnel.
8. Open the newly printed `https://....trycloudflare.com` URL.

Keep the Colab runtime running while using the application. If the runtime disconnects or stops, the temporary public URL expires. Rerun the notebook and use the newly generated URL.

**Colab security warning:** Cloudflare Quick Tunnel URLs are public and temporary. This starter app does not provide production-grade user authentication. Do not upload private, confidential, regulated, or client datasets to a publicly reachable Colab tunnel.

## 4. Add your own Power BI project and data

### Power BI project

Place a complete PBIP project folder under `powerbi/`, for example:

```text
powerbi/
  Sales Dashboard/
    dashboard.pbip
    dashboard.Report/
    dashboard.SemanticModel/
```

Keep the `.pbip` file and its `.Report` and `.SemanticModel` sibling folders together.

You can also upload a ZIP through the app's **Upload BI project** control. Zip the complete project folder and preserve its internal directory structure. The ZIP must contain a `.pbip` file.

### CSV / Excel data

Place exported tables in a matching folder under `data/`, for example:

```text
data/
  Sales Dashboard/
    Orders.csv
    OrderDetails.xlsx
    Products.xlsx
```

Each CSV is imported as a SQLite table. Each worksheet in an Excel workbook is imported as a table. Use exports from the same semantic model and keep table/column names consistent with the model.

For numerical data questions, the corresponding CSV/Excel data must be imported. PBIP metadata alone is not a substitute for the actual rows in the model.

## 5. Example questions

- What is the Net Sales by categories?
- Show monthly Net Sales as a line chart.
- Compare Sales and Profit by region.
- Which product category has the highest Net Sales?
- Explain the DAX definition of the Net Sales measure.
- List the relationships between Orders, OrderDetails and Products.

For charts, ask the assistant to return both a grouped data table and a chart. Chart rendering depends on the frontend's supported chart response format; if a chart is not rendered, request the underlying category/value table.

## 6. GitHub: upload or update this repository

Repository: https://github.com/vinay-kumar0901/Power-BI-chatbot

### Option A — GitHub website (no Git installation required)

1. Extract `Power-BI-chatbot.zip`.
2. Open the extracted `Power-BI-chatbot` folder.
3. Open https://github.com/vinay-kumar0901/Power-BI-chatbot.
4. Select **Add file → Upload files**.
5. Upload the *contents* of the extracted project folder (including `app`, `powerbi`, `data`, `knowledge`, `README.md`, `requirements.txt`, and `run_setup.py`) into the repository root.
6. Do not upload `.venv/`, `.env`, Python cache files, or local SQLite runtime databases.
7. Enter a commit message such as `Update BI-GPT chatbot`.
8. Select **Commit changes**.

If GitHub shows that a file already exists, upload the updated version and confirm the commit. Avoid uploading the entire project as a nested ZIP if you want GitHub to display and track the source files individually.

### Option B — Git command line

Open PowerShell in the extracted project folder. If the repository has already been cloned, use:

```powershell
git clone https://github.com/vinay-kumar0901/Power-BI-chatbot.git
cd Power-BI-chatbot
```

Then copy the updated project files into the cloned repository folder (not into an additional nested project folder), and run:

```powershell
git status
git add .
git commit -m "Update BI-GPT chatbot"
git push origin main
```

If your default branch is not `main`, replace `main` with the actual branch name shown on GitHub. If Git asks for authentication, complete the GitHub browser/device sign-in or use an authorized Git credential manager / personal access token. Never put a token in source code or `.env.example`.

## 7. What the application does — and limitations

- Chat history is stored locally in `storage/conversations.sqlite3`.
- PBIP/TMDL/model metadata and report JSON are scanned for tables, measures, relationships, pages and visual metadata where supported by the PBIP format.
- RAG retrieves relevant metadata and project knowledge.
- Ollama runs the language model locally (or inside the Colab runtime).
- SQL proposals are validated against imported SQLite schema and executed read-only.
- The app does **not** run the Power BI DAX engine. It cannot reproduce every DAX filter context, calculation group, row-level security rule, or Power BI Service behavior.
- Exact numerical answers require the corresponding CSV/Excel source data to be imported.
- The app does not edit PBIP files or publish reports to Power BI Service.
- AI-generated answers can be wrong. Verify important figures against Power BI.

## 8. Security and files not to commit

The `.gitignore` excludes the virtual environment, `.env`, Python cache, runtime SQLite databases, and uploaded files. Keep credentials and private data out of GitHub. Review the repository contents before every commit.

## 9. Troubleshooting

**`ollama` is not recognized:** Install Ollama, close and reopen PowerShell, then run `ollama --version`.

**Connection refused on port 11434:** Start the Ollama desktop service or run `ollama serve` in a separate terminal.

**Model not found:** Run `ollama pull llama3.2:1b` and retry.

**No numeric answer / missing table:** Confirm that the selected dashboard has its CSV/Excel exports under `data/<dashboard name>/` or upload the files through the app.

**Colab URL stopped working:** The runtime or tunnel probably stopped. Rerun the notebook and use the newly generated URL; old Quick Tunnel URLs are not permanent.

**Port 8000 is already in use locally:** Stop the other process using port 8000, or change the Uvicorn port and open the corresponding URL.
