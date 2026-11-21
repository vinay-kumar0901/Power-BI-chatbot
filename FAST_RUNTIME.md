# BI-GPT Fast Colab profile (3.6.0)

This profile uses llama3.2:1b, TF-IDF retrieval, a 3072-token context and bounded answer generation. CSV/Excel worksheets are read in parallel using a bounded process pool; SQLite writes remain serialized. Chat retrieval, conversation-history loading, and schema loading run concurrently with threads. Numerical-library thread counts are capped to reduce CPU oversubscription.

For faster inference, choose a Colab GPU runtime where available; Ollama detects supported GPU acceleration automatically. The 1B model is faster but less capable than 3B, so verify complex answers and SQL. The final notebook cell sends one question through the live app and reports latency and lightweight evaluation checks.

For the supplied PBIP, `[Net Sales]` is an explicit DAX measure in `Measure table.tmdl`: `[Sales After Line Discount] - [Order Discount Amount]`. It is calculated from `OrderDetails` and `Orders`, restricted to Completed and Shipped orders. The workbook summary column `Sales` is not treated as a replacement for the measure.
