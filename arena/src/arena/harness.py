"""Tournament loop — runs rounds, manages the agent population, coordinates phases."""

import json
import shutil
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

# Rotating authoring directives — one per round, cycles
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
    ):
        self.tournament_dir = tournament_dir
        self.agents_dir = tournament_dir / "agents"
        self.rounds_dir = tournament_dir / "rounds"
        self.challenges_dir = tournament_dir / "challenges"
        self.num_agents = num_agents
        self.challenges_per_round = challenges_per_round
        self.total_rounds = total_rounds
        self.llm = LLM()
        self.state = TournamentState()
        self.challenges: list[ChallengeSpec] = []
        self.all_solutions: dict[str, list[Solution]] = {}  # agent_id -> solutions

    def setup(self, baseline_dir: Path, seed_challenges_dir: Path) -> None:
        """Initialize tournament: create dirs, clone baseline agents, load seed challenges."""
        # Create directory structure
        self.tournament_dir.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(exist_ok=True)
        self.rounds_dir.mkdir(exist_ok=True)
        self.challenges_dir.mkdir(exist_ok=True)

        # Clone baseline agent N times
        for i in range(self.num_agents):
            agent_id = f"agent_{i:03d}"
            agent_dir = self.agents_dir / agent_id / "src" / "agent"
            agent_dir.mkdir(parents=True, exist_ok=True)
            # Copy baseline files
            for f in (baseline_dir / "src" / "agent").iterdir():
                if f.is_file():
                    shutil.copy2(f, agent_dir / f.name)
            self.state.agents.append(
                AgentInfo(id=agent_id, generation=0, source_dir=agent_dir)
            )

        # Load seed challenges
        if seed_challenges_dir.exists():
            for challenge_dir in sorted(seed_challenges_dir.iterdir()):
                if challenge_dir.is_dir():
                    try:
                        spec = challenges.load_challenge(challenge_dir)
                        # Copy to tournament challenges dir
                        challenges.save_challenge(spec, self.challenges_dir)
                        self.challenges.append(spec)
                        self.state.challenge_ids.append(spec.id)
                    except Exception as e:
                        print(f"Warning: Failed to load {challenge_dir}: {e}")

    def run(self) -> None:
        """Run the full tournament."""
        for round_num in range(1, self.total_rounds + 1):
            self.state.round_num = round_num
            display.show_tournament_header(
                round_num,
                self.total_rounds,
                len(self.state.agents),
                len(self.challenges),
            )

            result = self._run_round(round_num)
            self.state.history.append(result)

            # Save round data
            self._save_round(round_num, result)
            self._save_state()

            # Display results
            display.show_round_summary(result)
            display.show_leaderboard(result.fitness_reports)
            if self.all_solutions:
                display.show_technique_map(self.all_solutions)

    def _run_round(self, round_num: int) -> RoundResult:
        """Execute one tournament round: solve -> author -> score -> evolve."""
        result = RoundResult(round_num=round_num)
        round_solutions: dict[str, list[Solution]] = {}  # agent_id -> solutions this round

        # Select challenges for this round
        active_challenges = self.challenges[: self.challenges_per_round]
        if len(self.challenges) > self.challenges_per_round:
            # Rotate: use a sliding window
            start = (
                (round_num - 1) * self.challenges_per_round % len(self.challenges)
            )
            indices = [
                (start + i) % len(self.challenges)
                for i in range(min(self.challenges_per_round, len(self.challenges)))
            ]
            active_challenges = [self.challenges[i] for i in indices]

        # === SOLVE PHASE ===
        print(
            f"\n[Solve Phase] {len(self.state.agents)} agents x {len(active_challenges)} challenges"
        )
        for ag in self.state.agents:
            agent_solutions = []
            for challenge in active_challenges:
                try:
                    code = agent.solve(ag, challenge, self.llm)
                    passed, total, error_output, elapsed = challenges.run_tests(
                        code, challenge.test_code
                    )
                    sol = Solution(
                        agent_id=ag.id,
                        challenge_id=challenge.id,
                        code=code,
                        passed=passed,
                        total=total,
                        error_output=error_output,
                        elapsed_seconds=elapsed,
                    )
                except Exception as e:
                    sol = Solution(
                        agent_id=ag.id,
                        challenge_id=challenge.id,
                        code="",
                        error_output=str(e),
                    )
                agent_solutions.append(sol)
                print(f"  {ag.id} vs {challenge.id}: {sol.passed}/{sol.total}")
            round_solutions[ag.id] = agent_solutions

        self.all_solutions = round_solutions  # update for display

        # === AUTHOR PHASE ===
        print("\n[Author Phase]")
        directive = DIRECTIVES[(round_num - 1) % len(DIRECTIVES)]
        for ag in self.state.agents:
            new_challenge = None
            try:
                new_challenge = agent.author(
                    ag, self.challenges, round_solutions, self.llm
                )
                if new_challenge:
                    # Verify: author must solve their own challenge
                    verify_code = agent.solve(ag, new_challenge, self.llm)
                    passed, total, _, _ = challenges.run_tests(
                        verify_code, new_challenge.test_code
                    )
                    if passed > 0 and total > 0 and passed / total >= 0.5:
                        challenges.save_challenge(new_challenge, self.challenges_dir)
                        self.challenges.append(new_challenge)
                        self.state.challenge_ids.append(new_challenge.id)
                        result.new_challenges.append(new_challenge)
                        print(f"  {ag.id} authored: {new_challenge.title}")
                    else:
                        print(f"  {ag.id} authored challenge failed self-verify")
                        new_challenge = None
            except Exception as e:
                print(f"  {ag.id} author failed: {e}")
                new_challenge = None

        # === SCORE PHASE ===
        print("\n[Score Phase]")
        for ag in self.state.agents:
            sols = round_solutions.get(ag.id, [])

            # Solve score: average pass rate
            solve_score = (
                sum(s.pass_rate for s in sols) / len(sols) if sols else 0.0
            )

            # Novelty score: average AST novelty across solutions
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

            # Author score: based on whether authored challenge was accepted
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

        # === EVOLVE PHASE ===
        print("\n[Evolve Phase]")
        sorted_reports = sorted(
            result.fitness_reports, key=lambda r: r.total_score, reverse=True
        )
        new_agents = []

        for i, ag in enumerate(self.state.agents):
            report = next(r for r in sorted_reports if r.agent_id == ag.id)
            new_id = f"{ag.id}_g{ag.generation + 1}"
            new_agent = agent.clone_agent(
                ag, new_id, ag.generation + 1, self.agents_dir
            )

            # Evolve
            success = agent.evolve(new_agent, report, round_solutions, self.llm)
            if success:
                print(f"  {ag.id} evolved -> {new_id}")
            else:
                # Revert to parent on failed evolution
                print(f"  {ag.id} evolution failed, keeping current code")
                shutil.rmtree(
                    new_agent.source_dir.parent.parent, ignore_errors=True
                )
                new_agent = AgentInfo(
                    id=new_id,
                    generation=ag.generation + 1,
                    source_dir=ag.source_dir,
                    parent_id=ag.id,
                )

            # Random mutation (25% chance)
            if mutator.should_mutate():
                core_path = new_agent.source_dir / "core.py"
                if core_path.exists():
                    original = core_path.read_text()
                    mutated = mutator.mutate(original)
                    # Validate mutation
                    try:
                        compile(mutated, "<mutate>", "exec")
                        core_path.write_text(mutated)
                        print(f"  {new_id} mutated")
                    except SyntaxError:
                        print(f"  {new_id} mutation invalid, skipping")

            new_agents.append(new_agent)

        self.state.agents = new_agents
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

        # Append to summary.jsonl
        summary_file = self.tournament_dir / "summary.jsonl"
        with open(summary_file, "a") as f:
            for r in result.fitness_reports:
                line = json.dumps(
                    {
                        "round": round_num,
                        "agent": r.agent_id,
                        "solve": r.solve_score,
                        "author": r.author_score,
                        "novelty": r.novelty_score,
                        "total": r.total_score,
                    }
                )
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
        # Reload challenges
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
