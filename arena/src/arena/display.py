"""Rich terminal output for the Arena tournament."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from arena.models import FitnessReport, RoundResult, Solution

console = Console()

_RANK_COLORS = {1: "bold gold1", 2: "bold grey74", 3: "bold dark_goldenrod"}
_RANK_MEDALS = {1: "\u2655", 2: "\u2656", 3: "\u2657"}


def show_leaderboard(reports: list[FitnessReport]) -> None:
    """Display a ranked leaderboard table sorted by total_score descending."""
    ranked = sorted(reports, key=lambda r: r.total_score, reverse=True)

    table = Table(
        title="Leaderboard",
        title_style="bold bright_white",
        border_style="bright_blue",
        show_lines=False,
        pad_edge=True,
        padding=(0, 1),
    )
    table.add_column("Rank", justify="center", width=6)
    table.add_column("Agent", justify="left", min_width=12)
    table.add_column("Solve", justify="right", width=8)
    table.add_column("Author", justify="right", width=8)
    table.add_column("Novelty", justify="right", width=8)
    table.add_column("Total", justify="right", width=8)

    for i, report in enumerate(ranked, start=1):
        style = _RANK_COLORS.get(i, "")
        medal = _RANK_MEDALS.get(i, "")
        rank_display = f"{medal} {i}" if medal else str(i)

        table.add_row(
            Text(rank_display, style=style),
            Text(report.agent_id, style=style),
            Text(f"{report.solve_score:.2f}", style=style),
            Text(f"{report.author_score:.2f}", style=style),
            Text(f"{report.novelty_score:.2f}", style=style),
            Text(f"{report.total_score:.2f}", style=style or "bold bright_white"),
        )

    console.print()
    console.print(table)
    console.print()


def show_round_summary(result: RoundResult) -> None:
    """Display a panel summarizing the round."""
    reports = result.fitness_reports
    num_challenges = sum(
        len(r.solutions) for r in reports
    ) // max(len(reports), 1)
    new_count = len(result.new_challenges)

    top = max(reports, key=lambda r: r.total_score) if reports else None

    lines: list[str] = [
        f"[bright_blue]Challenges solved:[/] {num_challenges}",
        f"[bright_blue]New challenges authored:[/] {new_count}",
    ]
    if top:
        lines.append(
            f"[bright_blue]Top performer:[/] [bold bright_green]{top.agent_id}[/] "
            f"(score [bold]{top.total_score:.2f}[/])"
        )

    body = "\n".join(lines)
    panel = Panel(
        body,
        title=f"[bold]Round {result.round_num} Summary[/]",
        border_style="bright_blue",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def show_technique_map(solutions: dict[str, list[Solution]]) -> None:
    """Display a grid showing which agents solved which challenges.

    *solutions* maps challenge_id -> list of Solution objects.
    Cells are colored by pass_rate: green (100%), yellow (50-99%),
    red (<50% but >0%), dim dash (0% or missing).
    """
    if not solutions:
        console.print("[dim]No solutions to display.[/dim]")
        return

    # Collect all agent ids across every challenge.
    agent_ids: list[str] = sorted(
        {s.agent_id for sols in solutions.values() for s in sols}
    )

    table = Table(
        title="Technique Map",
        title_style="bold bright_white",
        border_style="bright_cyan",
        show_lines=True,
        pad_edge=True,
        padding=(0, 1),
    )
    table.add_column("Challenge", justify="left", min_width=14, style="bold")
    for agent_id in agent_ids:
        table.add_column(agent_id, justify="center", width=10)

    for challenge_id in sorted(solutions):
        sols = {s.agent_id: s for s in solutions[challenge_id]}
        cells: list[Text] = []
        for agent_id in agent_ids:
            sol = sols.get(agent_id)
            if sol is None or sol.pass_rate == 0:
                cells.append(Text("-", style="dim"))
            elif sol.pass_rate == 1.0:
                cells.append(Text(f"{sol.pass_rate:.0%}", style="bold bright_green"))
            elif sol.pass_rate >= 0.5:
                cells.append(Text(f"{sol.pass_rate:.0%}", style="bold yellow"))
            else:
                cells.append(Text(f"{sol.pass_rate:.0%}", style="bold red"))
        table.add_row(challenge_id, *cells)

    console.print()
    console.print(table)
    console.print()


def show_agent_detail(report: FitnessReport) -> None:
    """Show detailed breakdown for one agent."""
    table = Table(
        title=f"Agent Detail: {report.agent_id}",
        title_style="bold bright_white",
        border_style="bright_magenta",
        show_lines=False,
        pad_edge=True,
        padding=(0, 1),
    )
    table.add_column("Challenge", justify="left", min_width=14)
    table.add_column("Pass Rate", justify="right", width=10)
    table.add_column("Time (s)", justify="right", width=10)
    table.add_column("Status", justify="center", width=8)

    for sol in sorted(report.solutions, key=lambda s: s.challenge_id):
        rate = sol.pass_rate
        if rate == 1.0:
            rate_style = "bold bright_green"
            status = Text("PASS", style="bold bright_green")
        elif rate >= 0.5:
            rate_style = "bold yellow"
            status = Text("PARTIAL", style="bold yellow")
        elif rate > 0:
            rate_style = "bold red"
            status = Text("PARTIAL", style="bold red")
        else:
            rate_style = "dim"
            status = Text("FAIL", style="bold red")

        table.add_row(
            sol.challenge_id,
            Text(f"{rate:.0%}", style=rate_style),
            Text(f"{sol.elapsed_seconds:.3f}", style="cyan"),
            status,
        )

    # Summary scores
    summary_lines = (
        f"[bright_blue]Solve:[/]   {report.solve_score:.2f}    "
        f"[bright_blue]Author:[/]  {report.author_score:.2f}    "
        f"[bright_blue]Novelty:[/] {report.novelty_score:.2f}    "
        f"[bold bright_white]Total:[/]   [bold]{report.total_score:.2f}[/]"
    )

    console.print()
    console.print(table)
    console.print(Panel(summary_lines, border_style="bright_magenta", padding=(0, 2)))
    console.print()


def show_tournament_header(
    round_num: int,
    total_rounds: int,
    num_agents: int,
    num_challenges: int,
) -> None:
    """Display a header panel with tournament progress info."""
    progress_bar_width = 30
    filled = int(progress_bar_width * round_num / max(total_rounds, 1))
    bar = "[bright_green]" + "\u2588" * filled + "[/]" + "[dim]" + "\u2591" * (progress_bar_width - filled) + "[/]"

    body = (
        f"[bold bright_white]ARENA[/] \u2014 Adversarial Agent Evolution Tournament\n"
        f"\n"
        f"  Round  {bar}  [bold]{round_num}[/]/{total_rounds}\n"
        f"  Agents      [bold bright_cyan]{num_agents}[/]\n"
        f"  Challenges  [bold bright_cyan]{num_challenges}[/]"
    )

    panel = Panel(
        body,
        border_style="bright_blue",
        padding=(1, 3),
    )
    console.print()
    console.print(panel)
    console.print()
