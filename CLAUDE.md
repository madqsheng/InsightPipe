# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InsightPipe is a lightweight knowledge management tool that captures AI conversations and saves them as Markdown files. It consists of Python CLI scripts, a FastAPI backend, and a Vue 3 frontend.

## Quick Start

```bash
# Start all services
./start.sh

# Stop all services
./stop.sh

# View logs
tail -f server.log    # Backend logs
tail -f web.log       # Frontend logs
```

## Architecture

```
InsightPipe/
├── scripts/          # Python CLI tools
│   ├── ask.py        # Generate structured prompts, copy to clipboard
│   └── save.py       # Save AI responses to docs/
├── server/           # FastAPI backend (port 8817)
│   ├── main.py       # API endpoints
│   └── services/
│       └── gemini_service.py  # Import Gemini conversations
├── web/              # Vue 3 + Vite frontend (port 5817)
│   ├── src/
│   │   ├── components/
│   │   │   ├── PromptGenerator.vue
│   │   │   ├── DocEditor.vue
│   │   │   ├── DocGallery.vue
│   │   │   ├── DocReader.vue
│   │   │   └── GeminiImporter.vue
│   │   └── services/api.js
│   └── package.json
├── docs/             # Generated Markdown knowledge base
└── templates/
    └── base_prompt.txt   # 6-dimension analysis framework
```

## Commands

### Backend (FastAPI)
```bash
cd /home/sam/InsightPipe
python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8817
```

### Frontend (Vue 3)
```bash
cd /home/sam/InsightPipe/web
npm run dev      # Start dev server
npm run build    # Production build
```

### CLI Scripts
```bash
python scripts/ask.py "Your question"     # Generate prompt
python scripts/save.py "Topic Name"       # Save content
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/prompt/generate` | Generate prompt from template |
| POST | `/api/docs/save` | Save document |
| GET | `/api/docs` | List all documents |
| GET | `/api/docs/{filename}` | Get document content |
| DELETE | `/api/docs/{filename}` | Delete document |
| POST | `/api/import/gemini` | Import Gemini conversation |

## Key Flows

### 1. Ask Flow (CLI)
`ask.py` loads `templates/base_prompt.txt`, replaces `{{USER_INPUT}}`, copies to clipboard via `pyperclip`.

### 2. Save Flow (CLI)
`save.py` prompts for multi-line input (terminated by `EOF`), saves to `docs/{topic}.md`.

### 3. Gemini Import
1. Frontend `GeminiImporter.vue` sends share URL to `/api/import/gemini`
2. `gemini_service.py` fetches conversation via Google's batchexecute RPC
3. Parses response, extracts title/content, returns Markdown

### 4. Web UI Flow
1. User generates prompt via `PromptGenerator.vue`
2. Pastes into AI, copies response
3. Saves via `DocEditor.vue` → `/api/docs/save`
4. Views in `DocGallery.vue` → `DocReader.vue`

## Configuration

- **Backend port**: 8817
- **Frontend port**: 5817
- **Docs directory**: `docs/`
- **Templates directory**: `templates/`

## Environment Notes

- PID files (`.backend.pid`, `.frontend.pid`) are runtime artifacts, not tracked in git
- Logs are written to `server.log` and `web.log` (appended, not overwritten)
- The `docs/` directory is gitignored except for `.gitkeep`
