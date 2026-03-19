"""Tournament loop -- runs rounds, manages the agent population, coordinates phases."""

import json
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from arena.models import (
    AgentInfo,
    ChallengeSpec,
    FitnessReport,
    RoundResult,
    Solution,
    TournamentState,
)
from arena.llm import LLM
from arena import agent, challenges, mutator, display
from rich.live import Live

# Rotating authoring directives -- one per round, cycles
DIRECTIVES = [
    "Design a challenge that tests algorithmic thinking and requires O(n log n) or better.",
    "Create a challenge involving data structure design with specific performance constraints.",
    "Design a challenge that requires parsing or string processing with edge cases.",
    "Create a challenge involving graph or tree traversal with efficiency requirements.",
    "Design a challenge that tests dynamic programming or memoization skills.",
    "Create a challenge involving concurrent or stateful computation patterns.",
    "Design a challenge that requires mathematical reasoning and numerical methods.",
    "Create a challenge involving API design or protocol implementation.",
]


class Tournament:
    """Manages the full tournament lifecycle."""

    def __init__(
        self,
        tournament_dir: Path,
        num_agents: int = 4,
        challenges_per_round: int = 4,
        total_rounds: int = 20,
        max_workers: int = 8,
    ):
        self.tournament_dir = tournament_dir
        self.agents_dir = tournament_dir / "agents"
        self.rounds_dir = tournament_dir / "rounds"
        self.challenges_dir = tournament_dir / "challenges"
        self.num_agents = num_agents
        self.challenges_per_round = challenges_per_round
        self.total_rounds = total_rounds
        self.max_workers = max_workers
        self.llm = LLM()
        self.state = TournamentState()
        self.challenges: list[ChallengeSpec] = []
        self.all_solutions: dict[str, list[Solution]] = {}
        self.best_dir = tournament_dir / "best"
        self.best_scores: dict[str, float] = {}  # base_id -> best total_score

    def setup(self, baseline_dir: Path, seed_challenges_dir: Path) -> None:
        """Initialize tournament: create dirs, clone baseline agents, load seed challenges."""
        self.tournament_dir.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(exist_ok=True)
        self.rounds_dir.mkdir(exist_ok=True)
        self.challenges_dir.mkdir(exist_ok=True)

        for i in range(self.num_agents):
            agent_id = f"agent_{i:03d}"
            agent_dir = self.agents_dir / agent_id / "src" / "agent"
            agent_dir.mkdir(parents=True, exist_ok=True)
            for f in (baseline_dir / "src" / "agent").iterdir():
                if f.is_file():
                    shutil.copy2(f, agent_dir / f.name)
            self.state.agents.append(
                AgentInfo(id=agent_id, generation=0, source_dir=agent_dir)
            )

        if seed_challenges_dir.exists():
            for challenge_dir in sorted(seed_challenges_dir.iterdir()):
                if challenge_dir.is_dir():
                    try:
                        spec = challenges.load_challenge(challenge_dir)
                        challenges.save_challenge(spec, self.challenges_dir)
                        self.challenges.append(spec)
                        self.state.challenge_ids.append(spec.id)
                    except Exception as e:
                        display.console.print(
                            f"[yellow]Warning:[/] Failed to load {challenge_dir}: {e}"
                        )

    def run(self) -> None:
        """Run the full tournament."""
        start_round = self.state.round_num + 1
        for round_num in range(start_round, self.total_rounds + 1):
            self.state.round_num = round_num
            display.show_tournament_header(
                round_num, self.total_rounds,
                len(self.state.agents), len(self.challenges),
            )

            round_start = time.time()
            result = self._run_round(round_num)
            round_elapsed = time.time() - round_start

            self.state.history.append(result)
            self._save_round(round_num, result)
            self._save_state()

            display.show_round_summary(result)
            display.show_leaderboard(result.fitness_reports)
            if self.all_solutions:
                display.show_technique_map(self.all_solutions)
            display.show_token_usage(self.llm.token_usage)
            display.console.print(f"  [dim]Round completed in {round_elapsed:.1f}s[/]")

    def _run_round(self, round_num: int) -> RoundResult:
        """Execute one tournament round: solve -> author -> score -> evolve."""
        result = RoundResult(round_num=round_num)
        round_solutions: dict[str, list[Solution]] = {}

        # Select challenges: authored get priority, sample from full pool for rest
        import random
        authored = [c for c in self.challenges if c.source == "authored"]
        active_challenges = authored[:self.challenges_per_round]
        remaining = self.challenges_per_round - len(active_challenges)
        if remaining > 0 and self.challenges:
            others = [c for c in self.challenges if c not in active_challenges]
            if others:
                active_challenges += random.choices(others, k=remaining)
            else:
                active_challenges += random.choices(self.challenges, k=remaining)

        agent_ids = [ag.id for ag in self.state.agents]
        challenge_ids = [ch.id for ch in active_challenges]

        # === SOLVE PHASE (parallel with live display) ===
        n_tasks = len(self.state.agents) * len(active_challenges)
        display.show_phase_banner(
            "solve",
            f"{len(self.state.agents)} agents x {len(active_challenges)} challenges = {n_tasks} tasks"
        )

        solve_results: dict[tuple[str, str], Solution] = {}
        in_progress: set[tuple[str, str]] = set()
        lock = threading.Lock()
        t0 = time.time()

        def solve_one(ag: AgentInfo, ch: ChallengeSpec) -> Solution:
            key = (ag.id, ch.id)
            with lock:
                in_progress.add(key)
            try:
                code = agent.solve(ag, ch, self.llm)
                passed, total, error_output, elapsed = challenges.run_tests(
                    code, ch.test_code
                )
                return Solution(
                    agent_id=ag.id, challenge_id=ch.id, code=code,
                    passed=passed, total=total, error_output=error_output,
                    elapsed_seconds=elapsed,
                )
            except Exception as e:
                return Solution(
                    agent_id=ag.id, challenge_id=ch.id, code="",
                    error_output=str(e),
                )
            finally:
                with lock:
                    in_progress.discard(key)

        with Live(
            display.build_solve_display(
                agent_ids, challenge_ids, solve_results, in_progress,
                self.llm.token_usage,
            ),
            console=display.console,
            refresh_per_second=4,
        ) as live:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                for ag in self.state.agents:
                    for ch in active_challenges:
                        future = executor.submit(solve_one, ag, ch)
                        futures[future] = (ag, ch)

                for future in as_completed(futures):
                    ag, ch = futures[future]
                    sol = future.result()
                    with lock:
                        solve_results[(ag.id, ch.id)] = sol
                    live.update(
                        display.build_solve_display(
                            agent_ids, challenge_ids, solve_results, in_progress,
                            self.llm.token_usage,
                        )
                    )

        # Collect into per-agent lists
        for ag in self.state.agents:
            round_solutions[ag.id] = [
                solve_results[(ag.id, ch.id)] for ch in active_challenges
            ]
        self.all_solutions = round_solutions
        display.show_phase_complete("solve", time.time() - t0, f"[dim]{n_tasks} tasks[/]")

        # === AUTHOR PHASE (parallel) ===
        display.show_phase_banner(
            "author",
            f"{len(self.state.agents)} agents authoring challenges"
        )
        t0 = time.time()

        def author_one(ag: AgentInfo) -> tuple[AgentInfo, ChallengeSpec | None, bool]:
            try:
                new_ch = agent.author(ag, self.challenges, round_solutions, self.llm)
                if new_ch:
                    verify_code = agent.solve(ag, new_ch, self.llm)
                    passed, total, _, _ = challenges.run_tests(
                        verify_code, new_ch.test_code
                    )
                    if passed > 0 and total > 0 and passed / total >= 0.5:
                        return (ag, new_ch, True)
                    else:
                        return (ag, new_ch, False)
                return (ag, None, False)
            except Exception:
                return (ag, None, False)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            author_futures = {
                executor.submit(author_one, ag): ag
                for ag in self.state.agents
            }
            for future in as_completed(author_futures):
                ag, new_ch, accepted = future.result()
                if accepted and new_ch:
                    challenges.save_challenge(new_ch, self.challenges_dir)
                    self.challenges.append(new_ch)
                    self.state.challenge_ids.append(new_ch.id)
                    result.new_challenges.append(new_ch)
                display.show_author_result(
                    ag.id,
                    new_ch.title if new_ch else None,
                    accepted,
                )

        display.show_phase_complete(
            "author", time.time() - t0,
            f"[dim]{len(result.new_challenges)} accepted[/]"
        )

        # === SCORE PHASE (fast, no LLM calls) ===
        display.show_phase_banner("score", "Computing fitness scores")
        t0 = time.time()

        for ag in self.state.agents:
            sols = round_solutions.get(ag.id, [])

            solve_score = (
                sum(s.pass_rate for s in sols) / len(sols) if sols else 0.0
            )

            novelty_scores = []
            for sol in sols:
                if sol.code:
                    others = [
                        s.code
                        for aid, ss in round_solutions.items()
                        for s in ss
                        if aid != ag.id
                        and s.challenge_id == sol.challenge_id
                        and s.code
                    ]
                    nov = challenges.novelty_score(sol.code, others)
                    novelty_scores.append(nov)
            novelty = (
                sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0
            )

            author_score = 0.0
            authored = None
            for nc in result.new_challenges:
                if nc.author_id == ag.id:
                    author_score = 1.0
                    authored = nc
                    break

            total_score = 0.5 * solve_score + 0.3 * novelty + 0.2 * author_score

            report = FitnessReport(
                agent_id=ag.id,
                round_num=round_num,
                solve_score=solve_score,
                author_score=author_score,
                novelty_score=novelty,
                total_score=total_score,
                solutions=sols,
                authored_challenge=authored,
            )
            result.fitness_reports.append(report)

        display.show_phase_complete("score", time.time() - t0)

        # === BEST-CODE TRACKING ===
        self.best_dir.mkdir(exist_ok=True)
        for ag in self.state.agents:
            report = next(r for r in result.fitness_reports if r.agent_id == ag.id)
            base_id = ag.id.split("_g")[0]
            prev_best = self.best_scores.get(base_id, -1.0)
            if report.total_score > prev_best:
                self.best_scores[base_id] = report.total_score
                best_agent_dir = self.best_dir / base_id
                if best_agent_dir.exists():
                    shutil.rmtree(best_agent_dir)
                shutil.copytree(ag.source_dir, best_agent_dir)

        # === EVOLVE PHASE (parallel) ===
        display.show_phase_banner(
            "evolve", f"{len(self.state.agents)} agents evolving"
        )
        t0 = time.time()

        def evolve_one(
            ag: AgentInfo, report: FitnessReport
        ) -> tuple[int, AgentInfo, bool, bool]:
            """Returns (index, new_agent, evolution_success, was_mutated)."""
            idx = next(
                i for i, a in enumerate(self.state.agents) if a.id == ag.id
            )
            base_id = ag.id.split("_g")[0]
            new_id = f"{base_id}_g{ag.generation + 1}"

            # Evolve from best-performing code, not current (possibly broken) code
            best_agent_dir = self.best_dir / base_id
            evolve_source = ag
            if best_agent_dir.exists():
                evolve_source = AgentInfo(
                    id=ag.id, generation=ag.generation,
                    source_dir=best_agent_dir, parent_id=ag.parent_id,
                )

            new_agent = agent.clone_agent(
                evolve_source, new_id, ag.generation + 1, self.agents_dir
            )

            success = agent.evolve(new_agent, report, round_solutions, self.llm)
            if not success:
                shutil.rmtree(
                    new_agent.source_dir.parent.parent, ignore_errors=True
                )
                new_agent = AgentInfo(
                    id=new_id,
                    generation=ag.generation + 1,
                    source_dir=ag.source_dir,
                    parent_id=ag.id,
                )

            was_mutated = False
            if mutator.should_mutate():
                core_path = new_agent.source_dir / "core.py"
                if core_path.exists():
                    original = core_path.read_text()
                    mutated_code = mutator.mutate(original)
                    try:
                        compile(mutated_code, "<mutate>", "exec")
                        core_path.write_text(mutated_code)
                        was_mutated = True
                    except SyntaxError:
                        pass

            return (idx, new_agent, success, was_mutated)

        new_agents: list[AgentInfo | None] = [None] * len(self.state.agents)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            evolve_futures = {}
            for ag in self.state.agents:
                report = next(
                    r for r in result.fitness_reports if r.agent_id == ag.id
                )
                future = executor.submit(evolve_one, ag, report)
                evolve_futures[future] = ag

            for future in as_completed(evolve_futures):
                ag = evolve_futures[future]
                idx, new_agent, success, was_mutated = future.result()
                new_agents[idx] = new_agent
                display.show_evolve_result(
                    ag.id, new_agent.id, success, was_mutated
                )

        self.state.agents = [a for a in new_agents if a is not None]
        display.show_phase_complete("evolve", time.time() - t0)

        return result

    def _save_round(self, round_num: int, result: RoundResult) -> None:
        """Save round results to JSON."""
        round_file = self.rounds_dir / f"round_{round_num:03d}.json"
        data = {
            "round_num": round_num,
            "fitness_reports": [
                {
                    "agent_id": r.agent_id,
                    "solve_score": r.solve_score,
                    "author_score": r.author_score,
                    "novelty_score": r.novelty_score,
                    "total_score": r.total_score,
                    "solutions": [
                        {
                            "challenge_id": s.challenge_id,
                            "passed": s.passed,
                            "total": s.total,
                            "elapsed_seconds": s.elapsed_seconds,
                        }
                        for s in r.solutions
                    ],
                }
                for r in result.fitness_reports
            ],
            "new_challenges": [c.id for c in result.new_challenges],
        }
        round_file.write_text(json.dumps(data, indent=2))

        summary_file = self.tournament_dir / "summary.jsonl"
        with open(summary_file, "a") as f:
            for r in result.fitness_reports:
                line = json.dumps({
                    "round": round_num,
                    "agent": r.agent_id,
                    "solve": r.solve_score,
                    "author": r.author_score,
                    "novelty": r.novelty_score,
                    "total": r.total_score,
                })
                f.write(line + "\n")

    def _save_state(self) -> None:
        """Save current tournament state."""
        state_file = self.tournament_dir / "state.json"
        data = {
            "round_num": self.state.round_num,
            "agents": [
                {
                    "id": a.id,
                    "generation": a.generation,
                    "source_dir": str(a.source_dir),
                    "parent_id": a.parent_id,
                }
                for a in self.state.agents
            ],
            "challenge_ids": self.state.challenge_ids,
            "best_scores": self.best_scores,
        }
        state_file.write_text(json.dumps(data, indent=2))

    def load_state(self) -> bool:
        """Load existing tournament state. Returns True if state was loaded."""
        state_file = self.tournament_dir / "state.json"
        if not state_file.exists():
            return False
        data = json.loads(state_file.read_text())
        self.state.round_num = data["round_num"]
        self.state.agents = [
            AgentInfo(
                id=a["id"],
                generation=a["generation"],
                source_dir=Path(a["source_dir"]),
                parent_id=a.get("parent_id"),
            )
            for a in data["agents"]
        ]
        self.state.challenge_ids = data["challenge_ids"]
        self.best_scores = data.get("best_scores", {})
        self.challenges = []
        for cid in self.state.challenge_ids:
            cdir = self.challenges_dir / cid
            if cdir.exists():
                try:
                    self.challenges.append(challenges.load_challenge(cdir))
                except Exception:
                    pass
        return True

    def get_status(self) -> dict:
        """Return current tournament status as a dict."""
        return {
            "round": self.state.round_num,
            "total_rounds": self.total_rounds,
            "num_agents": len(self.state.agents),
            "num_challenges": len(self.challenges),
            "agents": [
                {"id": a.id, "generation": a.generation}
                for a in self.state.agents
            ],
            "token_usage": self.llm.token_usage,
        }
