"""Agent runtime — solve/author/evolve via Claude Code or API."""

from __future__ import annotations

import ast as _ast
import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

from arena.llm import LLM
from arena.models import AgentInfo, ChallengeSpec, FitnessReport, Solution


def _load_agent_module(agent: AgentInfo):
    """Dynamically load the agent's core.py module and return it."""
    core_path = agent.source_dir / "core.py"
    spec = importlib.util.spec_from_file_location("agent_core", core_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _use_claude_code() -> bool:
    """Check if claude CLI is available and not disabled."""
    if os.environ.get("ARENA_NO_CLAUDE_CODE") == "1":
        return False
    return shutil.which("claude") is not None


def _run_claude_code(prompt: str, workdir: Path) -> str:
    """Run a prompt through claude CLI and return the response."""
    result = subprocess.run(
        ["claude", "--print", "--dangerously-skip-permissions", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=workdir,
    )
    return result.stdout.strip()


def _run_api(llm: LLM, system: str, prompt: str) -> str:
    """Run a prompt through the Anthropic API."""
    return llm.complete(system=system, prompt=prompt)


def _extract_code(response: str) -> str:
    """Extract Python code from LLM response, stripping markdown fences if present."""
    text = response.strip()
    if text.startswith("```python"):
        text = text[len("```python"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


# ---------------------------------------------------------------------------
# Core agent actions
# ---------------------------------------------------------------------------


def solve(agent: AgentInfo, challenge: ChallengeSpec, llm: LLM) -> str:
    """Have an agent solve a challenge. Returns solution code string."""
    module = _load_agent_module(agent)
    prompt = module.solve_prompt(challenge.description, challenge.test_code)

    if _use_claude_code():
        response = _run_claude_code(prompt, agent.source_dir)
    else:
        response = _run_api(
            llm,
            "You are a Python programmer. Write only code, no explanation.",
            prompt,
        )

    return _extract_code(response)


def author(
    agent: AgentInfo,
    existing_challenges: list[ChallengeSpec],
    rival_solutions: dict[str, list[Solution]],
    llm: LLM,
) -> ChallengeSpec | None:
    """Have an agent author a new challenge. Returns ChallengeSpec or None if parsing fails."""
    module = _load_agent_module(agent)

    challenges_text = "\n".join(
        f"- {c.title}: {c.description[:100]}" for c in existing_challenges
    )
    solutions_text = ""
    for agent_id, sols in rival_solutions.items():
        for s in sols:
            solutions_text += (
                f"\n--- {agent_id} solving {s.challenge_id} ---\n{s.code[:500]}\n"
            )

    prompt = module.author_prompt(challenges_text, solutions_text)

    if _use_claude_code():
        response = _run_claude_code(prompt, agent.source_dir)
    else:
        response = _run_api(
            llm, "You are designing programming challenges.", prompt
        )

    return _parse_authored_challenge(response, agent.id)


def _parse_authored_challenge(response: str, author_id: str) -> ChallengeSpec | None:
    """Parse LLM response into a ChallengeSpec. Returns None if parsing fails."""
    try:
        lines = response.strip().split("\n")
        title = ""
        description_lines: list[str] = []
        difficulty = "medium"
        test_code_lines: list[str] = []
        in_description = False
        in_test_code = False

        for line in lines:
            if line.startswith("TITLE:"):
                title = line[len("TITLE:"):].strip()
                in_description = False
                in_test_code = False
            elif line.startswith("DESCRIPTION:"):
                description_lines = [line[len("DESCRIPTION:"):].strip()]
                in_description = True
                in_test_code = False
            elif line.startswith("DIFFICULTY:"):
                difficulty = line[len("DIFFICULTY:"):].strip().lower()
                in_description = False
                in_test_code = False
            elif line.startswith("TEST_CODE:"):
                in_test_code = True
                in_description = False
            elif line.strip() == "END_CHALLENGE":
                break
            elif in_test_code:
                test_code_lines.append(line)
            elif in_description:
                description_lines.append(line)

        if not title or not test_code_lines:
            return None

        # Generate a slug ID from the title
        challenge_id = title.lower().replace(" ", "_").replace("-", "_")
        challenge_id = "".join(c for c in challenge_id if c.isalnum() or c == "_")

        return ChallengeSpec(
            id=challenge_id,
            title=title,
            description="\n".join(description_lines),
            difficulty=difficulty,
            test_code="\n".join(test_code_lines),
            source="authored",
            author_id=author_id,
        )
    except Exception:
        return None


def evolve(
    agent: AgentInfo,
    report: FitnessReport,
    rival_solutions: dict[str, list[Solution]],
    llm: LLM,
) -> bool:
    """Have an agent evolve its own source code. Returns True if evolution succeeded."""
    module = _load_agent_module(agent)
    core_path = agent.source_dir / "core.py"
    own_source = core_path.read_text()

    # Format fitness report
    fitness_text = (
        f"Round: {report.round_num}\n"
        f"Solve score: {report.solve_score:.2f}\n"
        f"Author score: {report.author_score:.2f}\n"
        f"Novelty score: {report.novelty_score:.2f}\n"
        f"Total score: {report.total_score:.2f}\n"
    )
    for sol in report.solutions:
        fitness_text += (
            f"  {sol.challenge_id}: {sol.passed}/{sol.total}"
            f" ({sol.pass_rate:.0%})\n"
        )

    # Format rival solutions (exclude self)
    solutions_text = ""
    for agent_id, sols in rival_solutions.items():
        if agent_id == agent.id:
            continue
        for s in sols:
            solutions_text += (
                f"\n--- {agent_id} solving {s.challenge_id} ---\n{s.code[:500]}\n"
            )

    prompt = module.evolve_prompt(own_source, fitness_text, solutions_text)

    if _use_claude_code():
        response = _run_claude_code(prompt, agent.source_dir)
    else:
        response = _run_api(
            llm, "You are rewriting your own source code to improve.", prompt
        )

    new_source = _extract_code(response)

    # Validate the new source compiles
    try:
        compile(new_source, "<evolve>", "exec")
    except SyntaxError:
        return False

    # Check it still has the required functions
    try:
        tree = _ast.parse(new_source)
        func_names = {
            node.name
            for node in _ast.walk(tree)
            if isinstance(node, _ast.FunctionDef)
        }
        required = {"solve_prompt", "author_prompt", "evolve_prompt"}
        if not required.issubset(func_names):
            return False
    except Exception:
        return False

    # Write the new source
    core_path.write_text(new_source)

    # Handle additional files (FILE: filename.py pattern)
    _extract_additional_files(response, agent.source_dir)

    return True


def _extract_additional_files(response: str, source_dir: Path) -> None:
    """Extract and write additional files from FILE: markers in response."""
    lines = response.split("\n")
    current_file: str | None = None
    current_content: list[str] = []

    for line in lines:
        if line.startswith("FILE:"):
            if current_file and current_content:
                filepath = source_dir / current_file
                filepath.write_text("\n".join(current_content))
            current_file = line[len("FILE:"):].strip()
            current_content = []
        elif current_file is not None:
            current_content.append(line)

    if current_file and current_content:
        filepath = source_dir / current_file
        filepath.write_text("\n".join(current_content))


# ---------------------------------------------------------------------------
# Agent cloning
# ---------------------------------------------------------------------------


def clone_agent(
    source: AgentInfo,
    new_id: str,
    new_generation: int,
    agents_dir: Path,
) -> AgentInfo:
    """Clone an agent's source to create a new generation."""
    new_dir = agents_dir / new_id / "src" / "agent"
    new_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files from source agent
    for f in source.source_dir.iterdir():
        if f.is_file():
            shutil.copy2(f, new_dir / f.name)

    return AgentInfo(
        id=new_id,
        generation=new_generation,
        source_dir=new_dir,
        parent_id=source.id,
    )
