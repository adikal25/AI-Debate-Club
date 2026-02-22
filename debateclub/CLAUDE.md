# debateclub

CLI + web tool where two LLMs debate a topic via OpenRouter, scored by a judge model.

## Quick Start
```bash
# Set API key (or use .env file)
export OPENROUTER_API_KEY=your_key

# CLI mode
python -m debateclub "Pineapple belongs on pizza"

# Web UI mode
python -m debateclub --web
# Then visit http://localhost:8000
```

## Architecture
- All models go through OpenRouter via `openai` SDK
- Debaters run in parallel via `asyncio.gather`
- Judge receives formatted prose (not raw JSON)
- Output: rich terminal display + Markdown report in `debates/`
- Web UI: FastAPI + Jinja2 templates with vintage debate club aesthetic
- dotenv support: loads `.env` file automatically via `python-dotenv`

## Default Models
- FOR: `anthropic/claude-sonnet-4`
- AGAINST: `openai/gpt-4o`
- JUDGE: `google/gemini-2.0-flash-001`

## Web UI
- `--web` flag starts FastAPI server on port 8000
- `--host` and `--port` flags for custom binding
- Form lets you pick topic + models from dropdowns
- Results page shows winner, scorecard, and full arguments
