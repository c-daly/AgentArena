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


def _run_claude_code(prompt: str, workdir: Path, timeout: int = 300) -> str:
    """Run a prompt through claude CLI, piping prompt via stdin."""
    try:
        proc = subprocess.Popen(
            ["claude", "--print", "--dangerously-skip-permissions"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=workdir,
        )
        stdout, _ = proc.communicate(input=prompt, timeout=timeout)
        return stdout.strip()
    except subprocess.TimeoutExpired:
        proc.kill()
        return ""


def _run_api(llm: LLM, system: str, prompt: str) -> str:
    """Run a prompt through the Anthropic API."""
    return llm.complete(system=system, prompt=prompt)


def _extract_code(response: str) -> str:
    """Extract Python code from LLM response, stripping markdown fences and preamble."""
    import re
    match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r'```\n(.*?)```', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    lines = response.strip().splitlines()
    code_starts = ('import ', 'from ', 'def ', 'class ', '#')
    while lines and not lines[0].startswith(code_starts):
        lines.pop(0)
    return chr(10).join(lines).strip()



# ---------------------------------------------------------------------------
# Journal system — persistent per-agent memory across rounds
# ---------------------------------------------------------------------------

def _build_journal_entry(
    report: FitnessReport,
    rival_solutions: dict[str, list["Solution"]],
    agent_id: str,
) -> str:
    """Build a journal entry summarizing one round's results."""
    lines = [f"## Round {report.round_num}"]
    lines.append(f"Scores: solve={report.solve_score:.2f} author={report.author_score:.2f} novelty={report.novelty_score:.2f} total={report.total_score:.2f}")
    lines.append("")

    # What worked and what didn't
    for sol in report.solutions:
        status = "PASS" if sol.pass_rate == 1.0 else f"{sol.passed}/{sol.total}"
        lines.append(f"- {sol.challenge_id}: {status}")
        if sol.error_output and sol.pass_rate < 1.0:
            # One-line error summary
            err = sol.error_output.strip().splitlines()[-1][:120]
            lines.append(f"  Error: {err}")

    # One best rival technique per challenge (deduplicated)
    seen: set[str] = set()
    rival_notes = []
    for aid, sols in rival_solutions.items():
        if aid == agent_id:
            continue
        for s in sols:
            if not s.code or s.challenge_id in seen or s.pass_rate <= 0:
                continue
            if s.pass_rate > report.solutions[0].pass_rate if report.solutions else True:
                seen.add(s.challenge_id)
                # Extract just the key function signatures
                sig_lines = [l for l in s.code.splitlines()[:30] if l.startswith("def ") or l.startswith("class ")]
                if sig_lines:
                    rival_notes.append(f"- Rival approach for {s.challenge_id}: {', '.join(sig_lines[:3])}")

    if rival_notes:
        lines.append("")
        lines.append("Rival techniques worth studying:")
        lines.extend(rival_notes)

    lines.append("")
    return chr(10).join(lines)


def _append_journal(journal_path: Path, entry: str) -> None:
    """Append an entry to the agent's journal, keeping last 10 entries."""
    existing = ""
    if journal_path.exists():
        existing = journal_path.read_text()

    # Split into entries, keep last 9 + new one = 10
    entries = [e.strip() for e in existing.split("## Round") if e.strip()]
    entries = entries[-9:]  # keep last 9
    
    rebuilt = ""
    for e in entries:
        rebuilt += f"## Round{e}" + chr(10) + chr(10)
    rebuilt += entry

    journal_path.write_text(rebuilt)


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

    # Write journal entry and build evolve prompt from journal
    journal_path = agent.source_dir / "journal.md"
    entry = _build_journal_entry(report, rival_solutions, agent.id)
    _append_journal(journal_path, entry)

    journal = journal_path.read_text() if journal_path.exists() else ""
    prompt = module.evolve_prompt(own_source, journal, "")

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
