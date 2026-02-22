# debateclub

Two LLMs debate a topic. A third LLM judges. You pick the models.

Runs through [OpenRouter](https://openrouter.ai), so any model they support works — Claude, GPT-4o, Gemini, Llama, DeepSeek, etc.

## Setup

```bash
pip install -e .
```

You need an OpenRouter API key. Either export it or put it in a `.env` file:

```bash
export OPENROUTER_API_KEY=sk-or-...
```

## Usage

### CLI

```bash
python -m debateclub "Pineapple belongs on pizza"
```

Pick specific models:

```bash
python -m debateclub "Tabs vs spaces" \
  --for-model anthropic/claude-sonnet-4 \
  --against-model openai/gpt-4o \
  --judge-model google/gemini-2.0-flash-001
```

Output goes to the terminal (rich formatting) and a Markdown file in `debates/`.

### Web UI

```bash
python -m debateclub --web
```

Opens at `http://localhost:8000`. Pick a topic and models from dropdowns, get results on screen.

Custom host/port:

```bash
python -m debateclub --web --host 0.0.0.0 --port 3000
```

## How it works

1. Two models receive the topic and argue FOR and AGAINST (in parallel)
2. A judge model scores both on logic, evidence, and rhetoric (1-10 each)
3. Results: winner, scorecard, full arguments

## Default models

| Role | Model |
|------|-------|
| FOR | `anthropic/claude-sonnet-4` |
| AGAINST | `openai/gpt-4o` |
| JUDGE | `google/gemini-2.0-flash-001` |

## Project structure

```
debateclub/
├── cli.py          # argparse entry point
├── web.py          # FastAPI app
├── config.py       # DebateConfig + env loading
├── client.py       # OpenRouter client (openai SDK)
├── orchestrator.py # Debate flow (parallel args → judge)
├── judge.py        # Judge prompt + evaluation
├── models.py       # Pydantic schemas
├── prompts.py      # All prompt templates
├── report.py       # Markdown report generation
├── templates/      # Jinja2 HTML templates
└── static/         # CSS
```

## Requirements

- Python 3.11+
- OpenRouter API key
