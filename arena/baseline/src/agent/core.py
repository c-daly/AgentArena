"""Baseline agent core — naive single-shot prompts for solve, author, and evolve.

This agent is deliberately minimal. Evolution should improve every aspect.
"""


def solve_prompt(challenge_description: str, test_code: str) -> str:
    """Generate a prompt for solving a challenge.

    Takes the challenge description and test code, returns a system prompt
    that will be sent to the LLM. The LLM's response should be pure Python
    solution code (no markdown, no explanation).
    """
    return f"""You are a Python programmer. Solve this challenge.

Challenge: {challenge_description}

The test suite that will validate your solution:
```python
{test_code}
```

Write ONLY the Python solution code. No markdown, no explanation, no ```python blocks.
The tests import from your solution with `from solution import *`, so define all required functions at module level."""


def author_prompt(existing_challenges: str, rival_solutions: str) -> str:
    """Generate a prompt for authoring a new challenge.

    Takes descriptions of existing challenges and rival solutions.
    Returns a system prompt for the LLM. The LLM should return a YAML block
    with challenge metadata followed by a Python test suite.
    """
    return f"""You are designing a Python programming challenge for a tournament.

Existing challenges:
{existing_challenges}

Rival agents' recent solutions:
{rival_solutions}

Create a NEW challenge that tests a different skill than existing ones.
Your challenge should be solvable but require clever implementation.
Include efficiency tests that reject brute-force O(n²) solutions.

Respond in this exact format:

TITLE: <challenge title>
DESCRIPTION: <multi-line description of what to implement>
DIFFICULTY: <easy|medium|hard>
TEST_CODE:
<complete pytest test suite that does `from solution import *`>

END_CHALLENGE"""


def evolve_prompt(own_source: str, journal: str, _unused: str = "") -> str:
    """Generate a prompt for evolving the agent's own source code.

    Takes the agent's current source code and its journal (accumulated
    history of performance, errors, and rival techniques across rounds).
    Returns a prompt for the LLM to rewrite core.py.
    """
    return f"""You are an AI agent in a competitive tournament. You can rewrite your own source code to improve.

Your current source code:
```python
{own_source}
```

Your journal (history of your performance across rounds):
{journal}

Based on your journal, rewrite your source code (core.py) to perform better. Focus on:
- Fixing prompts that led to errors (check the Error lines in your journal)
- Learning from rival techniques mentioned in your journal
- Making your solve_prompt more specific about expected function signatures
- Making your author_prompt produce cleaner, more testable challenges

Write ONLY the complete new source code for core.py. No markdown, no explanation."""
