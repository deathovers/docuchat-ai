# API Documentation - DocuChat AI v1

The DocuChat AI API provides endpoints for document management and RAG-based chat interactions.

## Base URL
`http://localhost:8000/api/v1`

## Endpoints

### 1. Document Management

#### `POST /upload`
Uploads one or more PDF files to the current session.
- **Content-Type:** `multipart/form-data`
- **Input:** `files: List[UploadFile]`
- **Output:** `201 Created`
  ```json
  {
    "session_id": "uuid-string",
    "files": [
      {"file_id": "uuid-1", "filename": "report.pdf", "status": "Ready"}
    ]
  }
  ```

#### `GET /documents`
Lists all documents uploaded in the current session.
- **Output:** `200 OK`
  ```json
  [
    {
      "document_id": "uuid-1",
      "filename": "report.pdf",
      "upload_timestamp": "2026-03-06T10:00:00Z",
      "page_count": 12,
      "status": "Ready"
    }
  ]
  ```

#### `DELETE /documents/{file_id}`
Removes a specific document from the session and vector store.
- **Output:** `200 OK`

---

### 2. Chat Interface

#### `POST /chat`
Initiates a streaming RAG query.
- **Input:**
  ```json
  {
    "session_id": "string",
    "query": "What is the revenue for Q3?"
  }
  ```
- **Output:** `text/event-stream` (Server-Sent Events)

**Event Types:**
1.  `text`: Partial AI response tokens.
    ```json
    {"type": "text", "content": "The revenue for Q3 was..."}
    ```
2.  `citations`: Source references.
    ```json
    {"type": "citations", "content": [{"filename": "finance.pdf", "page": "4"}]}
    ```
3.  `error`: Error messages.
    ```json
    {"type": "error", "content": "Invalid session ID."}
    ```
4.  `done`: Signals the end of the stream.

---

## Security & Constraints
- **Session Sanitization:** All `session_id` inputs are sanitized to prevent directory traversal.
- **Rate Limiting:** Standard API rate limits apply.
- **File Size:** Maximum 20MB per PDF.
- **No OCR:** Only text-based PDFs are supported.
