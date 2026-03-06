# System Architecture - DocuChat AI

## 1. High-Level Design
DocuChat AI utilizes a Retrieval-Augmented Generation (RAG) architecture to provide grounded answers from user-uploaded PDFs.

## 2. Component Breakdown

### A. Ingestion Pipeline
- **Validation:** Ensures MIME type is `application/pdf`.
- **Extraction:** Uses `LlamaIndex` readers to parse PDF structure.
- **Chunking:** Recursive character splitting.
  - **Chunk Size:** 1000 tokens.
  - **Overlap:** 200 tokens.
- **Metadata:** Injects `file_name` and `page_label` into every chunk for citation accuracy.

### B. Vector Storage
- **Isolation:** Each `session_id` creates a unique subdirectory in the storage path.
- **Persistence:** Indices are saved to disk during the session but purged upon session end.
- **Sanitization:** `session_id` is regex-filtered (`[^a-zA-Z0-9_-]`) to prevent directory traversal attacks.

### C. RAG Engine (The Core)
The engine handles the coordination between the vector store and the LLM.
- **Async Processing:** Blocking disk I/O (loading indices) is offloaded to a thread pool using `asyncio.get_event_loop().run_in_executor`.
- **Streaming:** Uses `aquery` for asynchronous token generation.
- **Post-Processing:** Extracts source nodes from the LLM response to generate unique citations.

## 3. Data Flow
1. **User Uploads PDF** -> Backend saves to session folder -> LlamaIndex creates Vector Index.
2. **User Sends Query** -> Backend sanitizes session ID -> Loads Index from disk (Async) -> Performs Similarity Search (Top-K=5).
3. **LLM Generation** -> Context + Query sent to GPT-4o-mini -> Tokens streamed to UI via SSE.
4. **Citations** -> Metadata from retrieved chunks sent as a final JSON object in the stream.

## 4. Security Measures
- **Path Sanitization:** Prevents malicious users from accessing files outside their session directory.
- **Data Isolation:** No cross-pollination between user sessions.
- **Grounding:** System prompts enforce a "no-hallucination" policy.
