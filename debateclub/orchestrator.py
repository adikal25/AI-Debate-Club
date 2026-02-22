import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from debateclub.client import OpenRouterClient
from debateclub.config import DebateConfig
from debateclub.judge import evaluate
from debateclub.models import Argument, DebateResult
from debateclub.prompts import DEBATER_SYSTEM, DEBATER_USER
from debateclub.report import save_report

console = Console()


async def _argue(
    client: OpenRouterClient, model: str, topic: str, position: str
) -> Argument:
    """Have a model argue for or against a topic."""
    system = DEBATER_SYSTEM.format(position=position)
    user = DEBATER_USER.format(topic=topic, position=position)

    argument = await client.generate_parsed(
        model=model,
        system=system,
        user=user,
        schema=Argument,
    )
    argument.model_id = model
    return argument


async def run_debate(config: DebateConfig) -> DebateResult:
    """Run a full debate: two debaters in parallel, then a judge."""
    client = OpenRouterClient(api_key=config.openrouter_api_key)

    # Phase 1: Debaters argue in parallel
    console.print(
        Panel(f"[bold]{config.topic}[/bold]", title="Debate Topic", expand=False)
    )

    with console.status("[bold green]Debaters are arguing..."):
        for_arg, against_arg = await asyncio.gather(
            _argue(client, config.for_model, config.topic, "for"),
            _argue(client, config.against_model, config.topic, "against"),
        )

    console.print(f"[green]FOR[/green]  ({config.for_model}) — argument received")
    console.print(f"[red]AGAINST[/red] ({config.against_model}) — argument received")

    # Phase 2: Judge evaluates
    with console.status("[bold yellow]Judge is deliberating..."):
        judgment = await evaluate(
            client, config.judge_model, config.topic, for_arg, against_arg
        )

    # Build result
    result = DebateResult(
        topic=config.topic,
        for_argument=for_arg,
        against_argument=against_arg,
        judgment=judgment,
    )

    # Display results
    _display_results(result)

    # Save report
    path = save_report(result, config.output_dir)
    console.print(f"\n[dim]Report saved to {path}[/dim]")

    return result


def _display_results(result: DebateResult) -> None:
    """Display the debate results in a rich table."""
    judgment = result.judgment

    table = Table(title=f"Judgment by {judgment.model_id}")
    table.add_column("Category", style="bold")
    table.add_column("FOR", justify="center")
    table.add_column("AGAINST", justify="center")

    score_map_for = {s.category: s.score for s in judgment.for_scores}
    score_map_against = {s.category: s.score for s in judgment.against_scores}

    for_total = 0
    against_total = 0
    for category in ["logic", "evidence", "rhetoric"]:
        f_val = score_map_for.get(category, 0)
        a_val = score_map_against.get(category, 0)
        for_total += f_val
        against_total += a_val
        table.add_row(category.title(), str(f_val), str(a_val))

    table.add_row("[bold]Total[/bold]", f"[bold]{for_total}[/bold]", f"[bold]{against_total}[/bold]")

    console.print()
    console.print(table)

    # Winner announcement
    if judgment.winner == "tie":
        console.print("\n[bold yellow]Result: TIE[/bold yellow]")
    elif judgment.winner == "for":
        console.print(
            f"\n[bold green]Winner: FOR ({result.for_argument.model_id})[/bold green]"
        )
    else:
        console.print(
            f"\n[bold red]Winner: AGAINST ({result.against_argument.model_id})[/bold red]"
        )

    console.print(f"\n[dim]{judgment.reasoning}[/dim]")
