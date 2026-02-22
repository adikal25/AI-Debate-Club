from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from debateclub.config import DebateConfig
from debateclub.orchestrator import run_debate

BASE_DIR = Path(__file__).parent

app = FastAPI(title="The Debate Club")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

AVAILABLE_MODELS = [
    "anthropic/claude-sonnet-4",
    "openai/gpt-4o",
    "google/gemini-2.0-flash-001",
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4",
    "google/gemini-2.5-pro-preview-05-06",
    "meta-llama/llama-4-maverick",
    "deepseek/deepseek-chat-v3-0324",
]

DEFAULT_FOR = "anthropic/claude-sonnet-4"
DEFAULT_AGAINST = "openai/gpt-4o"
DEFAULT_JUDGE = "google/gemini-2.0-flash-001"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "models": AVAILABLE_MODELS,
            "default_for": DEFAULT_FOR,
            "default_against": DEFAULT_AGAINST,
            "default_judge": DEFAULT_JUDGE,
        },
    )


@app.post("/debate", response_class=HTMLResponse)
async def debate(
    request: Request,
    topic: str = Form(...),
    for_model: str = Form(...),
    against_model: str = Form(...),
    judge_model: str = Form(...),
) -> HTMLResponse:
    try:
        config = DebateConfig(
            topic=topic,
            for_model=for_model,
            against_model=against_model,
            judge_model=judge_model,
        )
        result = await run_debate(config)
        return templates.TemplateResponse(
            "results.html",
            {"request": request, "result": result},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "models": AVAILABLE_MODELS,
                "default_for": for_model,
                "default_against": against_model,
                "default_judge": judge_model,
                "topic": topic,
                "error": str(e),
            },
        )


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the web UI server."""
    import uvicorn

    print(f"Starting The Debate Club at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
