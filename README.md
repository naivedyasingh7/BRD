# BRD Genie 🧞

> AI-powered requirements engineering that turns chaotic conversations into audit-ready specifications — built for Bharat.

> ⚡ **Hackathon Prototype** — Built for rapid demo. Auth is mocked, DB is SQLite, no rate limiting.

---

## What it does

BRD Genie takes raw stakeholder voice notes, meeting recordings, or pasted text (in any Indian language) and runs them through a multi-agent AI pipeline to produce a complete, professional Business Requirements Document — with functional requirements, user stories, compliance checks, and regional language translation.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│  Splash → Auth → Dashboard → Workspace → Document   │
│              Vite dev server :3000                   │
│         proxies /api/* → FastAPI :8000               │
└────────────────────┬────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────┐
│                FastAPI Backend                       │
│  POST /api/start   →  LangGraph pipeline             │
│  POST /api/clarify →  Resume with user answers       │
│  GET  /api/history →  Past BRDs from SQLite          │
│  GET  /api/health  →  Server status                  │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              LangGraph Agent Pipeline                │
│                                                      │
│  Input Agent → Extract Agent → Clarify Agent         │
│       ↓ (questions?)                                 │
│  Pause & return questions to frontend                │
│       ↓ (answers submitted)                          │
│  BRD Agent → QA Agent → Localize Agent               │
└─────────────────────────────────────────────────────┘
```

### LangGraph Agent Flow

```
Voice/Text Input
      ↓
  Input Agent        — Sarvam STT + translation to English
      ↓
  Extract Agent      — CrewAI Discovery Crew (context → requirements → stakeholders)
      ↓                 Tasks chained with context= for coherent output
  Clarify Agent      — CrewAI Validation Crew (ambiguity detection → risk analysis)
      ↓
  Ambiguity found? ──Yes──▶ Pause → return questions to frontend
                              ↓ (user answers)
         No ──────────────▶ BRD Agent
                                ↓
                           QA Agent       — 10-point audit checklist, Indian compliance
                                ↓
                           Localize Agent — Sarvam AI chunked translation to target language
                                ↓
                           Final BRD (English + Localized)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend Framework | React 19 + TypeScript 5.8 |
| Build Tool | Vite 6.2 |
| Styling | Tailwind CSS v4 |
| Animation | Motion (Framer Motion) v12 |
| Backend Framework | FastAPI |
| Agent Orchestration | LangGraph |
| AI Agents | CrewAI |
| LLM | Groq (llama3-70b-8192) via CrewAI LLM |
| Speech-to-Text | Sarvam AI (`saaras:v1`) |
| Translation | Sarvam AI (`mayura:v1`) — chunked for large BRDs |
| Database | SQLite (via `brd_history.db`) |

---

## Project Structure

```
BRD/
├── backend/
│   ├── graph/
│   │   ├── agents.py        # All LangGraph node functions + CrewAI agents
│   │   ├── state.py         # BRDState TypedDict
│   │   └── workflow.py      # LangGraph StateGraph definition
│   ├── services/
│   │   ├── llm.py           # Shared CrewAI LLM singleton (Groq)
│   │   └── sarvam.py        # Sarvam AI STT + chunked translation service
│   ├── temp_audio/          # Uploaded audio files (auto-deleted after processing)
│   ├── database.py          # SQLite read/write helpers
│   └── main.py              # FastAPI app, routes, security headers, input validation
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AmbientCanvas.tsx    # Animated starfield canvas
│   │   │   ├── BrandLogo.tsx        # Animated SVG brand logo
│   │   │   ├── Navbar.tsx           # Floating pill navbar
│   │   │   ├── ShowcaseCarousel.tsx # Auto-advancing feature carousel
│   │   │   ├── ThemeToggle.tsx      # Light/dark toggle
│   │   │   ├── Toast.tsx            # Toast notification stack
│   │   │   └── UploadZone.tsx       # Drag-and-drop file upload (25MB limit)
│   │   ├── context/
│   │   │   └── AppContext.tsx       # Global state (nav, auth, projects, docs, toasts)
│   │   ├── views/
│   │   │   ├── SplashView.tsx       # Landing screen
│   │   │   ├── AuthView.tsx         # Sign in / Sign up (mocked for prototype)
│   │   │   ├── DashboardView.tsx    # Project portfolio
│   │   │   ├── WorkspaceView.tsx    # BRD compiler desk (backend connected)
│   │   │   ├── DocumentView.tsx     # Document editor & viewer
│   │   │   └── SettingsView.tsx     # Profile & preferences
│   │   ├── App.tsx                  # Route switcher with auth guard
│   │   ├── types.ts                 # Shared TypeScript types
│   │   └── index.css                # Design tokens, dark mode, global styles
│   ├── index.html                   # CSP meta tag included
│   ├── vite.config.ts               # Vite config with /api proxy to :8000
│   └── package.json
├── prompts/
│   ├── brd.txt              # BRD generation prompt — 10-section structure enforced
│   ├── extraction.txt       # Requirements extraction prompt — FR/NFR labelled
│   └── qa.txt               # QA review prompt — 10-point audit checklist
├── .env                     # Your API keys (not committed)
├── .env.example             # Template for .env
├── requirements.txt         # Python dependencies
└── start.sh                 # Single command to start everything
```

---

## Getting Started

### 1. Clone and configure

```bash
git clone <repo-url>
cd BRD
cp .env.example .env
```

Open `.env` and add your keys:

```env
GROQ_API_KEY=your_groq_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
```

| Key | Required | Get it at |
|---|---|---|
| `GROQ_API_KEY` | ✅ Required | [console.groq.com](https://console.groq.com) (free) |
| `SARVAM_API_KEY` | Optional | [dashboard.sarvam.ai](https://dashboard.sarvam.ai) — needed for audio STT and regional translation |

### 2. Start everything (single command)

```bash
./start.sh
```

This script automatically:
- Creates `.env` from example if missing
- Creates a Python venv and installs backend deps if missing
- Installs frontend `node_modules` if missing
- Starts the **backend** on `http://127.0.0.1:8000`
- Starts the **frontend** on `http://localhost:3000`
- `Ctrl+C` shuts down both cleanly

### 3. Or start manually (2 terminals)

**Terminal 1 — Backend:**
```bash
.venv/bin/uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Kill servers

```bash
pkill -f "uvicorn backend.main"; pkill -f "vite"
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Server status + `agents_ready` flag |
| `POST` | `/api/start` | Start BRD pipeline (text or audio file) |
| `POST` | `/api/clarify` | Submit answers to clarification questions |
| `GET` | `/api/history` | List all past generated BRDs |
| `GET` | `/api/history/{id}` | Get a specific BRD by ID |

### POST /api/start

Accepts `multipart/form-data`:

| Field | Type | Limit | Description |
|---|---|---|---|
| `raw_text` | string | 50,000 chars | Pasted text notes (any language) |
| `file` | file | 25 MB | Audio file (.wav, .mp3, .m4a) |
| `language` | string | — | Target output language (default: `English`) |

Returns the `BRDState` dict. If `questions` is non-empty and `answers` is empty, the pipeline has paused — display the questions and POST them to `/api/clarify`.

### POST /api/clarify

```json
{
  "state": { ...BRDState from /api/start response... },
  "answers": ["answer 1", "answer 2"]
}
```

Returns the completed `BRDState` with `final_brd` and `localized_brd`.

---

## BRD Output Structure

Every generated BRD contains these 10 sections:

1. Executive Summary
2. Project Objectives
3. Scope (In-Scope / Out-of-Scope)
4. Stakeholders (table)
5. Functional Requirements (REQ-1.0, REQ-2.0 … with acceptance criteria)
6. Non-Functional Requirements (Performance, Security, Scalability, Compliance)
7. Assumptions and Dependencies
8. Risks and Mitigations (table)
9. User Stories (As a… I want… so that…)
10. Acceptance Criteria Summary (table)

---

## Frontend Views

### Splash
Full-screen landing with animated starfield canvas, BRD Genie logo, and "Enter the Workspace" CTA.

### Auth (Sign In / Sign Up)
Split-card layout. **Note: auth is mocked for this prototype** — any credentials work. Sign Up includes password strength meter and terms checkbox.

### Dashboard
Project portfolio with search, status badges, activity feed, and a floating Genie search bar (⌘K).

### Workspace (BRD Compiler Desk)
The main generation view — connected to the real backend:
- Configure project name, stakeholders, and output language (9 Indian language presets)
- Upload audio or text files via drag-and-drop (25MB max)
- Live pipeline stepper: Transcription → Analysing → Writing
- Clarification panel appears automatically if the AI detects ambiguities
- Genie chat panel for conversational refinements after BRD is generated
- "Compile & Edit Draft" button to save and navigate to the document editor

### Document
Three-column document editor: TOC navigation, document content (all 10 BRD sections), and Genie suggestions sidebar. Includes collaborator comments, version history, and export to Jira / Confluence / Markdown.

### Settings
Profile editing, dark mode toggle, notification preferences, and sign out.

---

## Design System

### Color Tokens

| Token | Light | Dark |
|---|---|---|
| `--color-primary` | `#0D2137` | `#F0F0F0` |
| `--color-accent-gold` | `#1A78C2` | `#60B8F0` |
| `--color-bg-cream` | `#D6EAF8` | `#000000` |
| `--color-surface` | `#FFFFFF` | `#111111` |

### Typography
- **UI / Display**: Jost (geometric sans, 600)
- **Body**: Inter
- **Document content**: Playfair Display (serif)
- **Monospace / labels**: JetBrains Mono

### Dark Mode
Controlled by `.dark` class on `<html>`, toggled via `localStorage`.

---

## Supported Languages

English, Hindi, Tamil, Telugu, Bengali, Marathi, Kannada, Gujarati, Malayalam

---

## Prototype Limitations

These are known, intentional shortcuts for the hackathon:

| Limitation | Detail |
|---|---|
| **Auth is mocked** | Any email/password works. No real session management. |
| **SQLite database** | Fine for demo. Swap to PostgreSQL for production. |
| **No rate limiting** | `/api/start` and `/api/clarify` have no request throttling. |
| **Single-user state** | All projects stored in React context (resets on page refresh for new BRDs). |
| **Flowchart is static** | The SVG diagram in DocumentView is a placeholder, not generated from the BRD. |

---

## Notes

- Without `GROQ_API_KEY` the backend boots but returns `503` on generation endpoints.
- Without `SARVAM_API_KEY` audio upload is disabled and translation falls back to returning the English BRD as-is. Text input still works fully.
- Uploaded audio files are automatically deleted from `temp_audio/` after processing.
- The `/api` proxy in `vite.config.ts` forwards all frontend API calls to `http://127.0.0.1:8000` — no CORS issues in development.
