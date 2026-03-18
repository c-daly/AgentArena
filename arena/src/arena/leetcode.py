"""Fetch LeetCode problems via public GraphQL API and convert to arena challenges."""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

import requests

from arena.models import ChallengeSpec

if TYPE_CHECKING:
    from arena.llm import LLM

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

_PROBLEMSET_QUERY = """
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(categorySlug: $categorySlug, limit: $limit, skip: $skip, filters: $filters) {
    questions: data {
      title
      titleSlug
      difficulty
      content
    }
  }
}
"""

_QUESTION_DETAIL_QUERY = """
query questionDetail($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    titleSlug
    difficulty
    content
    exampleTestcases
    codeSnippets {
      lang
      langSlug
      code
    }
  }
}
"""

_TEST_GEN_SYSTEM = """\
You are an expert Python test engineer. You generate pytest test suites for \
programming challenges. Tests must import from solution using `from solution import *`. \
All functions must be standalone (no class Solution wrappers). \
Include efficiency tests with time bounds that reject brute-force O(n²) solutions \
when an O(n) or O(n log n) approach exists."""

_TEST_GEN_PROMPT = """\
Write a comprehensive pytest test suite for the following LeetCode problem.

## Problem
{description}

## Starter Code (convert to standalone function)
{starter_code}

## Requirements
1. Use `from solution import *` — no class wrappers.
2. Convert the LeetCode `class Solution` method to a standalone function. \
   For example, `def twoSum(self, nums, target)` becomes `def twoSum(nums, target)`.
3. Include basic correctness tests using the problem's examples.
4. Include edge case tests (empty inputs, single elements, large values, etc.).
5. Include at least one efficiency/performance test that generates a large input \
   and asserts the function completes within a reasonable time bound (use \
   `import time` and assert elapsed < threshold). The threshold should be generous \
   enough for correct algorithms but reject brute-force approaches.
6. Use plain `assert` statements or pytest features — no unittest.

Return ONLY the Python test code, no explanation. Start with the imports."""


def _warn(msg: str) -> None:
    """Print a warning to stderr."""
    print(f"[leetcode] WARNING: {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# HTML to text
# ---------------------------------------------------------------------------

_HTML_ENTITY_MAP = {
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
    "&apos;": "'",
    "&nbsp;": " ",
    "&#x27;": "'",
    "&#x2F;": "/",
}


def html_to_text(html: str) -> str:
    """Convert HTML to plain text using regex/string ops (no external libs)."""
    if not html:
        return ""

    text = html

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Block-level tags -> newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</div>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<div[^>]*>", "", text, flags=re.IGNORECASE)

    # List items
    text = re.sub(r"<li[^>]*>", "- ", text, flags=re.IGNORECASE)
    text = re.sub(r"</li>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?[ou]l[^>]*>", "\n", text, flags=re.IGNORECASE)

    # Headings
    for i in range(1, 7):
        text = re.sub(rf"<h{i}[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(rf"</h{i}>", "\n", text, flags=re.IGNORECASE)

    # Preserve pre/code content with newlines around them
    text = re.sub(r"<pre[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</pre>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<code[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</code>", "", text, flags=re.IGNORECASE)

    # Strong/em/b/i — just strip tags
    text = re.sub(r"</?(?:strong|em|b|i|u|span|a|sup|sub|font)[^>]*>", "", text, flags=re.IGNORECASE)

    # Strip any remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities
    for entity, char in _HTML_ENTITY_MAP.items():
        text = text.replace(entity, char)

    # Decode numeric entities (&#123; and &#x1a;)
    text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------------------------
# GraphQL fetchers
# ---------------------------------------------------------------------------

def fetch_problems(difficulty: str, limit: int) -> list[dict]:
    """Fetch a list of LeetCode problems by difficulty.

    Args:
        difficulty: One of 'easy', 'medium', 'hard'.
        limit: Maximum number of problems to return.

    Returns:
        List of dicts with keys: title, slug, difficulty, description.
    """
    variables = {
        "categorySlug": "",
        "limit": limit,
        "skip": 0,
        "filters": {"difficulty": difficulty.upper()},
    }

    try:
        resp = requests.post(
            LEETCODE_GRAPHQL_URL,
            json={"query": _PROBLEMSET_QUERY, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        _warn(f"Failed to fetch {difficulty} problems: {exc}")
        return []

    data = resp.json()
    questions = (
        data.get("data", {})
        .get("problemsetQuestionList", {})
        .get("questions", [])
    )

    results = []
    for q in questions:
        if q is None:
            continue
        results.append({
            "title": q.get("title", ""),
            "slug": q.get("titleSlug", ""),
            "difficulty": q.get("difficulty", difficulty).lower(),
            "description": html_to_text(q.get("content", "") or ""),
        })

    return results


def fetch_problem_detail(slug: str) -> dict:
    """Fetch full details for a single LeetCode problem by slug.

    Returns:
        Dict with keys: title, slug, description, starter_code, examples.

    Raises:
        ValueError: If the problem cannot be fetched.
    """
    variables = {"titleSlug": slug}

    try:
        resp = requests.post(
            LEETCODE_GRAPHQL_URL,
            json={"query": _QUESTION_DETAIL_QUERY, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ValueError(f"Failed to fetch problem '{slug}': {exc}") from exc

    data = resp.json()
    question = data.get("data", {}).get("question")
    if question is None:
        raise ValueError(f"Problem '{slug}' not found")

    # Extract Python3 code snippet
    starter_code = ""
    snippets = question.get("codeSnippets") or []
    for snippet in snippets:
        if snippet.get("langSlug") == "python3":
            starter_code = snippet.get("code", "")
            break

    return {
        "title": question.get("title", ""),
        "slug": slug,
        "description": html_to_text(question.get("content", "") or ""),
        "starter_code": starter_code,
        "examples": question.get("exampleTestcases", ""),
    }


# ---------------------------------------------------------------------------
# Challenge conversion
# ---------------------------------------------------------------------------

def _slug_to_id(slug: str) -> str:
    """Convert a LeetCode slug to a challenge ID (e.g. 'two-sum' -> 'two_sum')."""
    return re.sub(r"[^a-z0-9]+", "_", slug.lower()).strip("_")


def convert_to_challenge(problem: dict, llm: "LLM") -> ChallengeSpec:
    """Convert a LeetCode problem dict to a ChallengeSpec.

    Uses the LLM to generate a pytest test suite with efficiency benchmarks.

    Args:
        problem: Dict with keys: title, slug, description, starter_code.
        llm: LLM instance for test generation.

    Returns:
        A ChallengeSpec ready for the arena.

    Raises:
        ValueError: If test generation fails.
    """
    description = problem.get("description", "")
    starter_code = problem.get("starter_code", "")
    title = problem.get("title", problem.get("slug", "unknown"))
    slug = problem.get("slug", "unknown")
    difficulty = problem.get("difficulty", "medium").lower()

    prompt = _TEST_GEN_PROMPT.format(
        description=description,
        starter_code=starter_code,
    )

    raw_response = llm.complete(
        system=_TEST_GEN_SYSTEM,
        prompt=prompt,
        max_tokens=4096,
        temperature=0.4,
    )

    # Extract code from markdown fences if present
    test_code = raw_response.strip()
    fence_match = re.search(r"```python\s*\n(.*?)```", test_code, re.DOTALL)
    if fence_match:
        test_code = fence_match.group(1).strip()

    # Verify the test code imports from solution
    if "from solution import" not in test_code:
        test_code = "from solution import *\n\n" + test_code

    challenge_id = _slug_to_id(slug)

    return ChallengeSpec(
        id=challenge_id,
        title=title,
        description=description,
        difficulty=difficulty,
        test_code=test_code,
        source="leetcode",
        author_id=None,
    )


# ---------------------------------------------------------------------------
# Bootstrap entry point
# ---------------------------------------------------------------------------

def bootstrap(
    easy: int = 5,
    medium: int = 5,
    hard: int = 3,
    llm: "LLM | None" = None,
) -> list[ChallengeSpec]:
    """Fetch LeetCode problems and convert them to arena challenges.

    This is the main entry point for `arena bootstrap`.

    Args:
        easy: Number of easy problems to fetch.
        medium: Number of medium problems to fetch.
        hard: Number of hard problems to fetch.
        llm: LLM instance. If None, creates a default one.

    Returns:
        List of generated ChallengeSpecs.
    """
    if llm is None:
        from arena.llm import LLM as _LLM
        llm = _LLM()

    specs: list[ChallengeSpec] = []

    difficulty_counts = [
        ("easy", easy),
        ("medium", medium),
        ("hard", hard),
    ]

    for difficulty, count in difficulty_counts:
        if count <= 0:
            continue

        problems = fetch_problems(difficulty, count)
        if not problems:
            _warn(f"No {difficulty} problems fetched, skipping")
            continue

        for problem in problems:
            slug = problem.get("slug", "")
            try:
                # Fetch full details to get starter code
                detail = fetch_problem_detail(slug)
                # Merge difficulty from the list query
                detail["difficulty"] = problem.get("difficulty", difficulty)

                spec = convert_to_challenge(detail, llm)
                specs.append(spec)
            except Exception as exc:
                _warn(f"Failed to convert problem '{slug}': {exc}")
                continue

    return specs
