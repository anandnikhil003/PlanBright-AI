# PlanBright AI - Teaching Tools Platform

A full-stack AI-powered platform for educators, featuring lesson planning, assessment generation, rubric creation, differentiation suggestions, IEP generation, feedback generation, unit planning, and AI coaching.

## Repository Structure

```
planbright-ai/
├── backend/                 # FastAPI + Python backend
│   ├── agents/             # AI agent implementations
│   ├── routes/             # API endpoints
│   ├── models/             # Pydantic data models
│   ├── db/                 # Supabase database layer
│   ├── prompts/            # System prompts for AI agents
│   ├── config/             # Agent configurations & utilities
│   ├── security/           # Authentication
│   ├── personalization/    # Teacher/school data management
│   ├── bot/                # Bot management APIs
│   ├── data_ingestion/     # PDF processing pipeline
│   ├── main.py             # FastAPI app entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
│
└── frontend/               # React + TypeScript + Vite frontend
    ├── src/
    │   ├── components/     # Shared UI components (Layout, etc.)
    │   ├── context/        # React Context (Auth)
    │   ├── pages/          # Page components
    │   ├── api/            # API clients
    │   ├── App.tsx         # App routing
    │   └── main.tsx        # Entry point
    ├── public/             # Static assets
    ├── package.json        # Node dependencies
    ├── tsconfig.json       # TypeScript config
    ├── vite.config.ts      # Vite config
    └── .env.example        # Environment template
```

## Features

### Backend (FastAPI)
- **WebSocket** endpoints for interactive AI Coach chat
- **SSE (Server-Sent Events)** for streaming microapp responses
- **Supabase (PostgreSQL)** for data persistence
- **OpenAI + LlamaIndex + LangChain** for AI capabilities
- **Token-based authentication** via external auth provider
- **Export**: PDF, DOCX, Google Docs, Markdown

### Frontend (React + TypeScript)
- **Authentication**: Token-based login with localStorage persistence
- **Dashboard**: Overview of all available tools
- **Lesson Planner** (fully functional):
  - Form with grade, topic, standards, criteria
  - Real-time SSE streaming generation
  - History sidebar with favorites
  - Detail view with expand sections, quick actions, translate
  - Downloads: PDF, DOCX, Markdown
- **Resources tab**: All 8 agents (Lesson Planner, Assessment, Rubrik, Differentiation, IEP, Feedback, Unit Planner, AI Coach)
- **History page**: Filterable list of all generations
- **Settings**: Account info, API config

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account (for database)
- OpenAI API key (for AI agents)
- External auth provider (for token validation)

### Backend Setup
```bash
cd backend

# Copy environment template and fill in values
cp .env.example .env
# Edit .env with your credentials:
# - OPENAI_API_KEY
# - VALID_URL, AUTH_URL, PROFILE_URL (your auth provider)
# - SUPABASE_URL, SUPABASE_KEY
# - UC_BOT_DATA_DIRECTORY

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
# Runs on http://localhost:8000
# API docs: http://localhost:8000/api/docs
```

### Frontend Setup
```bash
cd frontend

# Copy environment template
cp .env.example .env
# Edit .env if backend runs elsewhere (default: http://localhost:8000)

# Install dependencies
npm install

# Run dev server
npm run dev
# Runs on http://localhost:5173
```

### Using Root Package Scripts
```bash
# Install all dependencies
npm run install:all

# Run backend
npm run dev:backend

# Run frontend (in separate terminal)
npm run dev:frontend

# Build frontend for production
npm run build:frontend
```

## Available Agents

| Agent | Endpoint | Status |
|-------|----------|--------|
| Lesson Planner | `/api/lesson_planner` | ✅ Functional |
| Assessment Generator | `/api/assesment_generator` | 🔜 Coming Soon |
| Rubrik Generator | `/api/rubrik_generator` | 🔜 Coming Soon |
| Differentiation Suggestor | `/api/diffrentiation_suggestor` | 🔜 Coming Soon |
| IEP Generator | `/api/iep_generator` | 🔜 Coming Soon |
| Feedback Generator | `/api/feedback_generator` | 🔜 Coming Soon |
| Unit Planner | `/api/unit_planner` | 🔜 Coming Soon |
| AI Coach | `/api/ai_coach` | 🔜 Coming Soon |

## Environment Variables

### Backend (`.env`)
```env
# Required
OPENAI_API_KEY=your_openai_key
VALID_URL=https://your-auth-provider/validate
AUTH_URL=https://your-auth-provider/activity
PROFILE_URL=https://your-auth-provider/profile
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
UC_BOT_DATA_DIRECTORY=./data

# Optional
HOST=0.0.0.0
PORT=8000
```

### Frontend (`.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Tech Stack

**Backend:**
- FastAPI, Uvicorn
- Supabase (PostgreSQL)
- OpenAI, LiteLLM, LlamaIndex, LangChain
- Python 3.10+

**Frontend:**
- React 18, TypeScript, Vite
- Tailwind CSS v4
- React Router v6
- Server-Sent Events (EventSource)

## License

MIT License - see [LICENSE.md](backend/LICENSE.md)
