"""Test execution, AST fingerprinting, and novelty scoring for Arena challenges."""

from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import yaml

from arena.models import ChallengeSpec, Solution


def run_tests(solution_code: str, test_code: str) -> tuple[int, int, str, float]:
    """Run a solution against a test suite in an isolated temp directory.

    Returns (passed, total, error_output, elapsed_seconds).
    """
    tmp_dir = tempfile.mkdtemp(prefix="arena_test_")
    try:
        solution_path = Path(tmp_dir) / "solution.py"
        test_path = Path(tmp_dir) / "test_solution.py"

        solution_path.write_text(solution_code, encoding="utf-8")
        test_path.write_text(test_code, encoding="utf-8")

        start = time.monotonic()
        try:
            result = subprocess.run(
                ["pytest", "test_solution.py", "-v", "--tb=short", "-p", "no:cacheprovider"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=tmp_dir,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            elapsed = time.monotonic() - start
            output = result.stdout + "\n" + result.stderr
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - start
            return 0, 1, "TIMEOUT: test execution exceeded 30 seconds", elapsed

        passed, total = _parse_pytest_output(output)
        error_output = output if passed < total else ""
        return passed, total, error_output, elapsed

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _parse_pytest_output(output: str) -> tuple[int, int]:
    """Extract passed/total counts from pytest verbose output.

    Handles summary lines like:
      "5 passed, 2 failed"
      "3 passed"
      "7 failed"
      "2 passed, 1 failed, 1 error"
    Falls back to counting individual test result lines.
    """
    # Look for the short test summary line: "= X passed, Y failed ... ="
    # or "= X passed ="
    summary_pattern = re.compile(
        r"=+\s*(.*?)\s*=+\s*$", re.MULTILINE
    )
    matches = summary_pattern.findall(output)

    for match in reversed(matches):  # last summary line is the final one
        counts: dict[str, int] = {}
        for count_match in re.finditer(r"(\d+)\s+(passed|failed|error|errors|warnings?|deselected|xfailed|xpassed|skipped)", match):
            key = count_match.group(2)
            counts[key] = int(count_match.group(1))

        if counts:
            passed = counts.get("passed", 0)
            failed = counts.get("failed", 0)
            errors = counts.get("error", 0) + counts.get("errors", 0)
            total = passed + failed + errors
            if total > 0:
                return passed, total

    # Fallback: count PASSED/FAILED lines from verbose output
    passed = len(re.findall(r" PASSED", output))
    failed = len(re.findall(r" FAILED", output))
    errored = len(re.findall(r" ERROR", output))
    total = passed + failed + errored

    if total > 0:
        return passed, total

    # If we couldn't parse anything, assume complete failure
    # (e.g. syntax error before collection, import error)
    if output.strip():
        return 0, 1
    return 0, 0


def ast_fingerprint(code: str) -> tuple[str, ...]:
    """Create a structural fingerprint of Python code via AST node types.

    Returns a tuple of AST node type names in walk order.
    Variable names, string literals, etc. are ignored — only structure matters.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ()

    return tuple(type(node).__name__ for node in ast.walk(tree))


def novelty_score(solution_code: str, other_solutions: list[str]) -> float:
    """Score how structurally unique a solution is compared to others.

    Returns 0.0 (identical structure) to 1.0 (completely novel).
    Uses Jaccard distance on AST node type multisets.
    """
    if not other_solutions:
        return 1.0

    fp = ast_fingerprint(solution_code)
    if not fp:
        return 0.0

    fp_set = set(fp)
    distances: list[float] = []

    for other_code in other_solutions:
        other_fp = ast_fingerprint(other_code)
        if not other_fp:
            distances.append(1.0)
            continue

        other_set = set(other_fp)
        intersection = fp_set & other_set
        union = fp_set | other_set

        if not union:
            distances.append(0.0)
        else:
            distances.append(1.0 - len(intersection) / len(union))

    return sum(distances) / len(distances)


def load_challenge(challenge_dir: Path) -> ChallengeSpec:
    """Load a ChallengeSpec from a challenge directory.

    Expects:
      challenge_dir/challenge.yaml
      challenge_dir/tests/test_solution.py
    """
    yaml_path = challenge_dir / "challenge.yaml"
    test_path = challenge_dir / "tests" / "test_solution.py"

    with open(yaml_path, encoding="utf-8") as f:
        meta = yaml.safe_load(f)

    test_code = test_path.read_text(encoding="utf-8")

    return ChallengeSpec(
        id=meta["id"],
        title=meta["title"],
        description=meta["description"],
        difficulty=meta["difficulty"],
        test_code=test_code,
        source=meta.get("source", "seed"),
        author_id=meta.get("author_id"),
    )


def save_challenge(challenge: ChallengeSpec, base_dir: Path) -> Path:
    """Save a ChallengeSpec to disk as a challenge directory.

    Creates:
      base_dir/<challenge.id>/challenge.yaml
      base_dir/<challenge.id>/tests/test_solution.py

    Returns the challenge directory path.
    """
    challenge_dir = base_dir / challenge.id
    tests_dir = challenge_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "difficulty": challenge.difficulty,
        "source": challenge.source,
    }
    if challenge.author_id is not None:
        meta["author_id"] = challenge.author_id

    yaml_path = challenge_dir / "challenge.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(meta, f, default_flow_style=False, sort_keys=False)

    test_path = tests_dir / "test_solution.py"
    test_path.write_text(challenge.test_code, encoding="utf-8")

    return challenge_dir
