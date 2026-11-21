# BI-GPT Advanced 3.8.0

## Fixed
- Render assistant Markdown tables as real HTML tables.
- Render bold, italic, headings, lists, inline code and fenced SQL blocks.
- Escape untrusted response text before adding formatting, preventing raw HTML/script injection through model output.
- Keep the Net Sales DAX-to-SQL calculation unchanged; this is a UI rendering release.

## Validation
- All Python source files pass `py_compile`.
- The embedded browser JavaScript passes `node --check`.
- End-to-end Ollama/SQLite execution still needs to be run in the target Colab runtime with its installed dependencies and active Ollama service.
