# BI-GPT 3.3.0 — Colab tunnel reliability build

This release uses a fresh Cloudflare Quick Tunnel on every notebook run. Quick Tunnel URLs are temporary: if a Colab runtime stops, its URL expires and can later return DNS_PROBE_FINISHED_NXDOMAIN. Always use the URL printed by the final cell of the current runtime.

The notebook starts cloudflared with HTTP/2, waits for the new hostname, checks DNS and `/api/health`, and retries with QUIC if the first tunnel cannot become reachable. The application remains on port 8000.

The app uses TF-IDF retrieval by default and Ollama for answer generation. Keep the Colab runtime active while using the temporary URL.


## 3.6.0

The Colab notebook adds bounded parallel Excel-sheet/CSV reads, concurrent chat retrieval/history/schema tasks, a single-question end-to-end evaluation cell, and DAX-aligned Net Sales SQL.
