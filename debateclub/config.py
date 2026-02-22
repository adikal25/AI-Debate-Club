import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class DebateConfig:
    topic: str
    for_model: str = "anthropic/claude-sonnet-4"
    against_model: str = "openai/gpt-4o"
    judge_model: str = "google/gemini-2.0-flash-001"
    output_dir: str = "debates"
    openrouter_api_key: str = ""

    def __post_init__(self) -> None:
        if not self.openrouter_api_key:
            key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("API_KEY", "")
            if not key:
                raise ValueError(
                    "OPENROUTER_API_KEY environment variable is required. "
                    "Get one at https://openrouter.ai/keys"
                )
            self.openrouter_api_key = key
