"""Data models for the Arena tournament system."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChallengeSpec:
    """A programming challenge with test suite."""

    id: str
    title: str
    description: str
    difficulty: str  # "easy", "medium", "hard"
    test_code: str
    source: str = "seed"  # "seed", "authored", "leetcode"
    author_id: str | None = None


@dataclass
class Solution:
    """An agent's solution to a challenge."""

    agent_id: str
    challenge_id: str
    code: str
    passed: int = 0
    total: int = 0
    error_output: str = ""
    elapsed_seconds: float = 0.0

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0


@dataclass
class FitnessReport:
    """Fitness evaluation for an agent in a round."""

    agent_id: str
    round_num: int
    solve_score: float = 0.0
    author_score: float = 0.0
    novelty_score: float = 0.0
    total_score: float = 0.0
    solutions: list[Solution] = field(default_factory=list)
    authored_challenge: ChallengeSpec | None = None


@dataclass
class AgentInfo:
    """Agent metadata and location."""

    id: str
    generation: int
    source_dir: Path
    parent_id: str | None = None


@dataclass
class RoundResult:
    """Results from a single tournament round."""

    round_num: int
    fitness_reports: list[FitnessReport] = field(default_factory=list)
    new_challenges: list[ChallengeSpec] = field(default_factory=list)


@dataclass
class TournamentState:
    """Current state of the tournament."""

    round_num: int = 0
    agents: list[AgentInfo] = field(default_factory=list)
    challenge_ids: list[str] = field(default_factory=list)
    history: list[RoundResult] = field(default_factory=list)
