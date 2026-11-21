# BI-GPT Architecture

## End-to-end flow
1. User asks a question in the FastAPI chat interface.
2. Sentence Transformers encodes the question using `sentence-transformers/all-MiniLM-L6-v2`.
3. FAISS searches the business knowledge documents.
4. Vectors are L2-normalized and searched using inner product, which is equivalent to cosine similarity for normalized vectors.
5. Supported numerical questions are mapped to fixed, allowlisted SQL templates.
6. SQLite calculates the exact numerical result.
7. Retrieved documentation and the verified SQL result are sent to the optional LLM.
8. The LLM explains the result; if unavailable, deterministic SQL output is returned.

## Components
- Embeddings: Sentence Transformers `sentence-transformers/all-MiniLM-L6-v2`
- Vector index: FAISS `IndexFlatIP`
- Retrieval: cosine similarity
- LLM: Ollama or OpenAI-compatible chat endpoint
- Numerical database: SQLite
- Backend: FastAPI

## Trust boundaries
RAG retrieves definitions, schema and business rules. SQL calculates figures. User text is never executed as SQL. Only fixed query templates are allowed.
