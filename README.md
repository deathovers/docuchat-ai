# DocuChat AI

DocuChat AI is a high-performance Retrieval-Augmented Generation (RAG) platform that allows users to interact with multiple PDF documents simultaneously. By leveraging advanced vector embeddings and LLMs, it provides accurate, grounded answers with verifiable citations.

## 🚀 Project Overview
DocuChat AI is designed for speed, security, and accuracy. It processes PDF documents, chunks them with context-aware strategies, and stores them in a session-isolated vector space. Users can then query their documents and receive streaming responses with page-level citations.

### Key Features
- **Multi-Document Support:** Upload up to 10 PDFs per session.
- **Strict Grounding:** AI responses are strictly limited to the provided context to eliminate hallucinations.
- **Streaming Responses:** Real-time token streaming for a responsive chat experience.
- **Page-Level Citations:** Every answer includes references to the source filename and page number.
- **Session Isolation:** Data is strictly scoped to the user session and purged upon termination.
- **Performance Optimized:** Non-blocking I/O and asynchronous processing ensure < 5s response times.

## 🛠 Tech Stack
- **Backend:** FastAPI (Python 3.10+)
- **Orchestration:** LlamaIndex
- **LLM:** GPT-4o-mini / Claude 3.5 Sonnet
- **Embeddings:** OpenAI `text-embedding-3-small`
- **PDF Processing:** PyMuPDF / PDFPlumber
- **Vector Store:** Local FAISS/ChromaDB (Session-scoped)

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/docuchat-ai.git
   cd docuchat-ai
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_api_key_here
   STORAGE_DIR=./storage
   LOG_LEVEL=INFO
   ```

## 🏃 Usage

1. **Start the Backend Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the API:**
   The API will be available at `http://localhost:8000`. You can view the interactive Swagger docs at `http://localhost:8000/docs`.

## 🏗 Architecture

DocuChat AI follows a modular RAG architecture:
1. **Ingestion Layer:** Validates PDFs, extracts text, and performs recursive character splitting (1000 token chunks, 200 token overlap).
2. **Indexing Layer:** Generates embeddings and stores them in a session-specific directory.
3. **Retrieval Layer:** Performs Top-K (K=5) similarity search based on user queries.
4. **Generation Layer:** Augments the LLM prompt with retrieved context and streams the response via Server-Sent Events (SSE).

---
*Date: March 6, 2026*
