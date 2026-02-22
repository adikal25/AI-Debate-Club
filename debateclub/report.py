import os
import re
from pathlib import Path

from debateclub.models import DebateResult


def generate_report(result: DebateResult) -> str:
    """Generate a Markdown report from a DebateResult."""
    for_arg = result.for_argument
    against_arg = result.against_argument
    judgment = result.judgment

    # Calculate totals
    categories = ["logic", "evidence", "rhetoric"]
    for_total = sum(s.score for s in judgment.for_scores if s.category in categories)
    against_total = sum(s.score for s in judgment.against_scores if s.category in categories)

    # Build score rows
    score_map_for = {s.category: s for s in judgment.for_scores}
    score_map_against = {s.category: s for s in judgment.against_scores}

    score_rows = []
    for category in ["logic", "evidence", "rhetoric"]:
        f_score = score_map_for.get(category)
        a_score = score_map_against.get(category)
        f_val = f_score.score if f_score else "-"
        a_val = a_score.score if a_score else "-"
        score_rows.append(f"| {category.title()} | {f_val} | {a_val} |")

    score_table = "\n".join(score_rows)

    # Determine winner display
    if judgment.winner == "tie":
        winner_line = "Tie"
    elif judgment.winner == "for":
        winner_line = f"FOR ({for_arg.model_id})"
    else:
        winner_line = f"AGAINST ({against_arg.model_id})"

    # Format claims
    def format_claims(claims: list) -> str:
        parts = []
        for i, c in enumerate(claims, 1):
            parts.append(
                f"{i}. **{c.assertion}** — {c.evidence} → {c.reasoning}"
            )
        return "\n".join(parts)

    report = f"""\
# Debate: {result.topic}
_{result.timestamp.strftime("%Y-%m-%d %H:%M:%S")}_

## FOR: {for_arg.model_id}

{for_arg.opening_statement}

### Claims

{format_claims(for_arg.claims)}

{for_arg.conclusion}

## AGAINST: {against_arg.model_id}

{against_arg.opening_statement}

### Claims

{format_claims(against_arg.claims)}

{against_arg.conclusion}

## Judgment by {judgment.model_id}

| Category | FOR | AGAINST |
|----------|-----|---------|
{score_table}
| **Total** | **{for_total}** | **{against_total}** |

### Winner: {winner_line}

{judgment.reasoning}
"""
    return report


def save_report(result: DebateResult, output_dir: str) -> Path:
    """Save the debate report to a Markdown file and return the path."""
    os.makedirs(output_dir, exist_ok=True)

    # Sanitize topic for filename
    slug = re.sub(r"[^\w\s-]", "", result.topic.lower())
    slug = re.sub(r"[\s]+", "_", slug.strip())[:50]
    timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"{slug}_{timestamp}.md"

    path = Path(output_dir) / filename
    path.write_text(generate_report(result))
    return path
