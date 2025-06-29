# ✉️ AI-Powered Cover Letter Generator

Generate confident, tailored cover letters in seconds using AI! Upload your resume (PDF, DOCX, or TXT) and a job description, and get a professional, human-like cover letter—instantly.

---

## 🚀 Features
- **Multi-format Resume Support:** Upload PDF, Word (.docx), or plain text resumes
- **Streaming Generation:** See your cover letter generated in real time
- **AI-Powered:** Uses Anthropic Claude for high-quality, context-aware writing
- **Customizable Tone:** Choose from professional, confident, conversational, and more
- **Honest & Confident Output:** No fabricated experience, always positive and tailored
- **Feedback Loop:** Suggest improvements and regenerate with your feedback
- **Modern UI:** Built with Next.js, Tailwind CSS, and Framer Motion
- **Observability:** Langfuse-powered tracing and analytics

---

## 🧰 Tech Stack
- **Frontend:** Next.js (React, TypeScript, Tailwind CSS)
- **Backend:** FastAPI (Python), LangGraph for workflow orchestration
- **AI:** Anthropic Claude (Opus/Sonnet)
- **Cache:** Redis
- **Observability:** Langfuse
- **Deployment:** Vercel (frontend), Render (backend)

---

## 🏗️ Architecture
```
[User] ⇄ [Next.js Frontend] ⇄ [FastAPI Backend] ⇄ [LangGraph Workflow]
                                              ⇂
                                         [Anthropic Claude]
                                              ⇂
                                         [Redis, Langfuse]
```
- **Frontend:** Handles file uploads, streaming responses, and user feedback
- **Backend:** Validates files, extracts text, matches experiences, generates and validates cover letters
- **LangGraph:** Orchestrates multi-step workflow (parse, match, generate, validate)
- **AI:** Generates cover letters with confidence and honesty

---

## ⚡ Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/coverletter.git
cd coverletter
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your Anthropic, Redis, Langfuse keys
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd ../coverletter-frontend
npm install
cp .env.local.example .env.local  # Set NEXT_PUBLIC_API_URL to your backend
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## 🌐 Deployment
- **Frontend:** Deploy to Vercel. Set `NEXT_PUBLIC_API_URL` to your Render backend URL in Vercel dashboard.
- **Backend:** Deploy to Render. Set all required environment variables (see `.env.example`).
- **CORS:** Make sure your backend allows your frontend domain.

---

## 📝 Contributing
Pull requests welcome! Please open an issue first to discuss major changes.

---

## 📸 Screenshots
_Add screenshots or a demo video here!_

---

## 📄 License
MIT
