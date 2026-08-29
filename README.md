# CampusMind — AI-Powered College Information Assistant (RAG Chatbot)

CampusMind is an enterprise-grade Retrieval-Augmented Generation (RAG) system engineered to answer student and faculty questions about college admissions, courses, fees, exams, academic calendars, hostel rules, and policies.

---

## 🌟 Key Features

1. **Strict Context Grounding**: The chatbot answers **strictly** from uploaded institutional documents. If context is missing, it explicitly returns a fallback:
   > *"I don't have information about that in the college documents. You may want to contact the relevant department directly."*
2. **Transparent Source Attribution**: Every response includes source document titles, exact page numbers, text snippets, and relevance scores.
3. **Role-Based Access Control (RBAC)**:
   - **Student**: Access to the conversational chatbot interface, past history, feedback buttons (👍/👎), and suggested question chips.
   - **Admin**: Knowledge base management dashboard to upload (PDF, DOCX, TXT), view status, version, and delete documents.
4. **Universal Embedding & Vector Search**:
   - Built with support for PostgreSQL + `pgvector` or automatic lightweight vector similarity fallback.
   - Supports OpenAI (`text-embedding-3-small` / `gpt-4o-mini`), HuggingFace local models (`sentence-transformers/all-MiniLM-L6-v2`), and zero-dependency offline mode.

---

## 🏗️ System Architecture

```
┌───────────────────────────┐         ┌───────────────────────────┐
│     Next.js Frontend      │ ◄─────► │      FastAPI Backend      │
│  (React 18 + Tailwind CSS)│         │     (Python 3.11+)        │
└───────────────────────────┘         └─────────────┬─────────────┘
                                                    │
                                      ┌─────────────┴─────────────┐
                                      │  PostgreSQL / Vector DB   │
                                      │ (Documents & Chunks Store)│
                                      └───────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

---

### 2. Backend Setup & Run

1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. *(Optional)* Configure environment variables:
   - Copy `.env.example` to `.env` in the project root:
     ```bash
     cp ../.env.example .env
     ```
   - If you have an OpenAI API key, set `OPENAI_API_KEY=your_key` and `USE_LOCAL_EMBEDDINGS=false` inside `.env`.

5. **Seed the database with sample college documents and demo users**:
   ```bash
   python seed.py
   ```
   *This automatically creates default demo users and chunks/embeds sample college documents (`Admission_Brochure_2026.txt`, `Hostel_Rules_Policy.txt`, `Academic_Calendar_2026.txt`).*

6. **Start the FastAPI Backend Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Docs will be available at: **http://127.0.0.1:8000/docs**

---

### 3. Frontend Setup & Run

1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   - Frontend will be live at: **http://localhost:3000**

---

## 🔑 Default Demo Accounts

| Role | Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Student** | `student@campusmind.edu` | `student123` | Chat UI, Conversation History, Source Citations, Feedback |
| **Admin** | `admin@campusmind.edu` | `admin123` | Full Chat UI + Document Upload & Management Dashboard |

---

## 📡 Key API Endpoints

### 🔐 Authentication
- `POST /api/auth/signup` — Create student or admin account
- `POST /api/auth/login` — Login and receive JWT access & refresh tokens
- `POST /api/auth/refresh` — Refresh access token

### 💬 Chat & RAG
- `POST /api/chat/message` — Send question, returns answer, sources, confidence, answered status
- `GET /api/chat/conversations` — List user conversation history
- `GET /api/chat/conversations/{id}` — Fetch conversation messages and source citations
- `POST /api/chat/message/{id}/feedback` — Submit thumbs up / down feedback

### 🛡️ Admin & Knowledge Base
- `POST /api/admin/documents/upload` — Upload PDF/DOCX/TXT for parsing, chunking, and embedding
- `GET /api/admin/documents` — List all uploaded documents with status
- `DELETE /api/admin/documents/{id}` — Delete document and associated vector chunks

---

## 🧪 Testing the RAG Pipeline

Try asking these verified questions in the chat:
1. *"What is the minimum PCM aggregate required for B.Tech CSE admission?"*
2. *"What are the curfew timings for hostels on weekends?"*
3. *"When are the Autumn 2026 Mid-Semester Examinations scheduled?"*
4. *"Who is the Prime Minister of France?"* *(Notice the strict fallback triggering because it is outside college documentation)*
