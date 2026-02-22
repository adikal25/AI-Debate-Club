import argparse
import asyncio
import sys

from debateclub.config import DebateConfig
from debateclub.orchestrator import run_debate


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="debateclub",
        description="Two LLMs debate a topic, a judge scores them.",
    )
    parser.add_argument("topic", nargs="?", help="The debate topic")
    parser.add_argument(
        "--for-model",
        default="anthropic/claude-sonnet-4",
        help="Model arguing FOR (default: anthropic/claude-sonnet-4)",
    )
    parser.add_argument(
        "--against-model",
        default="openai/gpt-4o",
        help="Model arguing AGAINST (default: openai/gpt-4o)",
    )
    parser.add_argument(
        "--judge-model",
        default="google/gemini-2.0-flash-001",
        help="Judge model (default: google/gemini-2.0-flash-001)",
    )
    parser.add_argument(
        "--output-dir",
        default="debates",
        help="Directory for debate reports (default: debates/)",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the web UI instead of CLI mode",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Web UI host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Web UI port (default: 8000)",
    )

    args = parser.parse_args(argv)

    if not args.web and not args.topic:
        parser.error("a topic is required unless using --web")

    return args


def main(argv: list[str] | None = None) -> None:
    try:
        args = parse_args(argv)
    except SystemExit:
        raise
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.web:
        from debateclub.web import serve

        serve(host=args.host, port=args.port)
        return

    config = DebateConfig(
        topic=args.topic,
        for_model=args.for_model,
        against_model=args.against_model,
        judge_model=args.judge_model,
        output_dir=args.output_dir,
    )

    try:
        asyncio.run(run_debate(config))
    except KeyboardInterrupt:
        print("\nDebate cancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
