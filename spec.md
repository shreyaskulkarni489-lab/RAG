College RAG Chatbot — Technical Specification
1. Overview
Project Name: CampusMind (working title) — AI-powered College Information Assistant
Type: Retrieval-Augmented Generation (RAG) chatbot
Purpose: Answer student and staff questions about admissions, departments, courses, fees, exams, academic calendar, hostel, library, clubs, placements, scholarships, policies, and events — grounded strictly in uploaded college documents.
Core Principle: The LLM never answers from its own general knowledge. Every answer must be derived from retrieved document chunks. If no relevant chunk is found above a confidence threshold, the system must explicitly say the information isn't available.
---
2. Tech Stack
Layer	Technology	Notes
Frontend	React (Next.js) + Tailwind CSS	Chat UI, auth pages, admin dashboard
Backend / API	FastAPI (Python 3.11+)	REST API, async, serves both chat and admin routes
Auth	JWT (access + refresh tokens) via `python-jose` + `passlib` (bcrypt)	Roles: `student`, `admin`
Relational DB	PostgreSQL 15+	Users, documents metadata, chat history, feedback
Vector DB	`pgvector` extension on the same Postgres instance (default) — OR Chroma/Pinecone as swappable alternative	One DB to manage instead of two, unless scale demands a dedicated vector store
Document Parsing	`PyMuPDF` (`fitz`) for PDFs, `python-docx` for Word docs	Extracts text + page numbers for source citation
Chunking	Custom recursive splitter (LangChain `RecursiveCharacterTextSplitter` or hand-rolled)	~500–800 tokens/chunk, ~15% overlap
Embeddings	`text-embedding-3-small` (OpenAI) — OR `sentence-transformers/all-MiniLM-L6-v2` (free/local fallback)	1536-dim (OpenAI) or 384-dim (local)
LLM	GPT-4o-mini / Claude Haiku (API) — OR local via Ollama (Llama 3) for zero-cost dev	Swappable via config/env var
Orchestration	LangChain or a thin custom RAG layer (recommended: custom, for control + fewer dependencies)	
File Storage	Local disk (`/uploads`) for dev, S3-compatible bucket for prod	Original PDFs kept for source-link display
Deployment	Frontend → Vercel; Backend → Render/Railway; DB → managed Postgres (Supabase/Neon/Render)	
Realtime	Server-Sent Events (SSE) or streaming HTTP response	For streaming AI answers (bonus feature)
---
3. System Architecture
```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Frontend   │◄────►│   FastAPI     │◄────►│   PostgreSQL     │
│  (Next.js)   │      │   Backend     │      │  + pgvector      │
└─────────────┘      └──────┬───────┘      └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              ┌─────▼─────┐      ┌──────▼──────┐
              │ Embedding  │      │     LLM      │
              │  Service   │      │   Service    │
              │ (OpenAI/   │      │ (OpenAI/     │
              │  local)    │      │  Claude/     │
              │            │      │  Ollama)     │
              └────────────┘      └──────────────┘
```
3.1 Ingestion Pipeline (Admin side)
```
Upload Document → Validate (type/size) → Extract Text (page-aware)
→ Chunk (with overlap) → Generate Embeddings → Store chunk + vector + metadata
→ Mark document status: "processed"
```
3.2 Query Pipeline (Student side)
```
User Question → Embed Question → Vector Similarity Search (top-k, filtered by
collection/department if applicable) → Filter by relevance score threshold
→ Build Context Prompt (chunks + chat history) → LLM Call
→ Parse Answer + Attach Sources → Stream to Frontend → Log to Chat History
```
---
4. Data Models (Postgres Schema)
`users`
Field	Type	Notes
id	UUID (PK)	
name	varchar	
email	varchar (unique)	
password_hash	varchar	
role	enum(`student`,`admin`)	
created_at	timestamp	
`documents`
Field	Type	Notes
id	UUID (PK)	
title	varchar	
filename	varchar	original filename
file_path	varchar	storage path/URL
department	varchar (nullable)	for department-wise KBs
collection	varchar (nullable)	e.g. "Admissions", "Hostel"
uploaded_by	UUID (FK → users)	
status	enum(`processing`,`processed`,`failed`)	
version	int	for version management
created_at	timestamp	
`document_chunks`
Field	Type	Notes
id	UUID (PK)	
document_id	UUID (FK → documents)	
chunk_text	text	
chunk_index	int	order within doc
page_number	int (nullable)	for source display
embedding	vector(1536)	pgvector column
created_at	timestamp	
`conversations`
Field	Type	Notes
id	UUID (PK)	
user_id	UUID (FK → users)	
title	varchar	auto-generated from first message
created_at	timestamp	
`messages`
Field	Type	Notes
id	UUID (PK)	
conversation_id	UUID (FK → conversations)	
role	enum(`user`,`assistant`)	
content	text	
sources	jsonb (nullable)	list of {document_id, title, page, snippet, score}
feedback	enum(`up`,`down`,null)	bonus feature
created_at	timestamp	
---
5. RAG Pipeline Details
5.1 Chunking Strategy
Chunk size: 500–800 tokens
Overlap: ~15% (75–120 tokens) to preserve context across boundaries
Split on paragraph/section boundaries where possible before falling back to hard token splits
Each chunk retains: `document_id`, `page_number`, `chunk_index`
5.2 Retrieval
Top-k = 4–6 chunks per query (configurable)
Similarity metric: cosine similarity
Relevance threshold: if the top result's score is below a set cutoff (e.g. 0.75 depending on embedding model), treat as "no relevant context found"
Optional filters: `department`, `collection` (for department-wise or topic-scoped search)
5.3 Prompt Template (system-level)
```
You are a college information assistant. Answer the student's question
using ONLY the context provided below. Do not use outside knowledge.

If the context does not contain enough information to answer, respond:
"I don't have information about that in the college documents. You may
want to contact the relevant department directly."

Context:
{retrieved_chunks}

Conversation history:
{last_n_turns}

Question: {user_question}

Answer concisely, and reference which document/section supports your answer.
```
5.4 Unknown-Question Handling
If no chunk clears the relevance threshold → skip LLM call, return fallback message directly (saves cost, guarantees no hallucination)
If chunks are retrieved but LLM judges them insufficient → LLM is instructed to say so explicitly rather than guess
---
6. API Endpoints (Backend)
Auth
`POST /api/auth/signup`
`POST /api/auth/login`
`POST /api/auth/refresh`
Chat
`POST /api/chat/message` → send question, returns answer + sources (supports streaming)
`GET /api/chat/conversations` → list user's past conversations
`GET /api/chat/conversations/{id}` → get full message history
`POST /api/chat/message/{id}/feedback` → 👍/👎 (bonus)
Documents (Admin)
`POST /api/admin/documents/upload`
`GET /api/admin/documents`
`DELETE /api/admin/documents/{id}`
`PUT /api/admin/documents/{id}` → update/replace (versioning)
`GET /api/admin/documents/{id}/status` → processing status
Analytics (bonus)
`GET /api/admin/analytics/queries` → most-asked questions, unanswered queries, feedback stats
---
7. Output Format (Chat Response)
Every assistant response returned to the frontend follows this JSON shape:
```json
{
  "answer": "The B.Tech CSE admission requires a minimum of 60% in PCM...",
  "sources": [
    {
      "document_title": "Admission_Brochure_2026.pdf",
      "page_number": 4,
      "snippet": "Eligibility: minimum 60% aggregate in PCM...",
      "relevance_score": 0.87
    }
  ],
  "confidence": "high",
  "answered": true
}
```
When unanswerable:
```json
{
  "answer": "I don't have information about that in the college documents. You may want to contact the relevant department directly.",
  "sources": [],
  "confidence": "none",
  "answered": false
}
```
---
8. Non-Functional Requirements
Document processing (extraction → embedding) should complete within a reasonable time for files up to ~50MB; large files processed asynchronously with status polling
Chat response latency target: first token within ~2s (streaming)
All admin document operations logged (who uploaded/deleted/updated, when)
Passwords hashed (bcrypt); JWT secrets in environment variables, never hardcoded
---
9. Milestones / Build Order
Postgres schema + pgvector setup
Document upload → extraction → chunking → embedding pipeline (script-level, no UI)
Vector search endpoint (standalone, testable via API client)
Full RAG pipeline: retrieval + prompt construction + LLM call + fallback handling
Chat UI + JWT auth (student + admin roles)
Admin document management dashboard (upload/list/delete/version)
Chat history + conversation context
Bonus features (priority order): streaming responses, source highlighting, feedback buttons, suggested questions, department-wise collections, admin analytics
---
10. Bonus Features — Implementation Notes
Feature	Approach
Multiple/department-wise collections	`collection`/`department` column on `documents`, filter at retrieval time
Source highlighting	Store char offsets of matched chunk within page text; highlight in frontend viewer
Confidence/relevance score	Return top chunk's cosine similarity score alongside answer
Multilingual	Detect language of query, translate to English for retrieval, respond in original language
Streaming responses	SSE from FastAPI, token-by-token render on frontend
Hybrid search	Combine pgvector cosine search with Postgres full-text search (`tsvector`), merge/re-rank results
Document re-ranking	Add a lightweight cross-encoder re-rank pass on top-k before sending to LLM
Role-based access	Extend `role` enum if department-scoped admins are needed
OCR for scanned PDFs	`pytesseract` fallback when `PyMuPDF` text extraction returns near-empty text
