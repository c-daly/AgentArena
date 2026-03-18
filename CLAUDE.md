# Arena — Adversarial Agent Evolution Tournament

## What this is

A tournament system where multiple AI agents compete to solve and author Python programming challenges. Agents see each other's solutions, evolve by rewriting their own source code, and are subject to random mutations. The system selects for both correctness and efficiency.

## Project layout

```
arena/
├── pyproject.toml              # installable package, entry point: arena CLI
├── src/arena/
│   ├── cli.py                  # CLI: arena run, arena bootstrap, arena status
│   ├── harness.py              # Tournament loop — runs rounds, manages population
│   ├── agent.py                # Agent runtime — solve/author/evolve via Claude Code or API
│   ├── challenges.py           # Test execution (pytest in subprocess), AST fingerprinting, novelty scoring
│   ├── leetcode.py             # Fetches LeetCode problems via GraphQL, converts to natural Python challenges
│   ├── mutator.py              # Random source code mutations (epsilon for exploration)
│   ├── models.py               # Dataclasses: ChallengeSpec, Solution, FitnessReport, etc.
│   ├── llm.py                  # Thin Anthropic API wrapper with token tracking
│   └── display.py              # Rich terminal output — leaderboards, technique maps
├── baseline/                   # Gen-0 agent template — deliberately minimal
│   └── src/agent/
│       ├── __init__.py
│       └── core.py             # Naive single-shot solve/author/evolve prompts
├── seed_challenges/            # Starting challenge pool
│   ├── 001_smart_cache/        # LRU cache with TTL + efficiency benchmarks
│   │   ├── challenge.yaml
│   │   └── tests/test_solution.py
│   ├── 002_expression_eval/    # Recursive descent parser + efficiency benchmarks
│   │   ├── challenge.yaml
│   │   └── tests/test_solution.py
│   └── 003_schema_validator/   # Recursive schema validation + efficiency benchmarks
│       ├── challenge.yaml
│       └── tests/test_solution.py
└── tournament/                 # Created at runtime by `arena run`
    ├── agents/                 # Agent directories per generation
    ├── rounds/                 # JSON logs per round
    ├── summary.jsonl           # Append-only fitness history
    └── state.json              # Current tournament state
```

## How it works

### Each round:
1. **Solve phase**: Every agent solves every challenge. Tests run in isolated temp dirs via pytest subprocess. Tests include efficiency benchmarks with time bounds — brute-force O(n²) solutions fail.
2. **Author phase**: Every agent creates a new challenge + solution. The harness verifies the author can solve their own challenge before accepting it. Valid challenges join the pool permanently.
3. **Score phase**: Pass rate (correctness + efficiency), novelty (AST distance from other solutions), author quality.
4. **Evolve phase**: Each agent sees its own fitness report + ALL rival solutions. It rewrites its own source code. 25% chance of additional random mutation.

### Agent runtime (agent.py):
- Auto-detects `claude` CLI. If present, agents run as Claude Code sessions with CLAUDE.md.
- Falls back to direct Anthropic API calls if CLI not available.
- Set `ARENA_NO_CLAUDE_CODE=1` to force API mode.

### Challenge format:
Each challenge is a directory with `challenge.yaml` (metadata) and `tests/test_solution.py` (pytest suite). Tests do `from solution import *`. Solutions are standalone Python — no class wrappers.

### LeetCode bootstrap (leetcode.py):
Fetches problems via public GraphQL API, converts to natural Python (standalone functions, not `class Solution`), uses LLM to generate test suites with efficiency benchmarks.

## Key design decisions

- **Efficiency is tested, not measured separately.** Test suites include time-bounded benchmarks that generate large inputs. A slow solution just fails more tests.
- **Full visibility.** After each round, every agent sees every other agent's complete solution code. This is how innovations propagate.
- **Random mutation (epsilon).** Most mutations break things. That's fine — broken agents get reverted. The rare mutations that work are discoveries nobody would have searched for deliberately.
- **Authored challenges are adversarial.** Agents study rivals' code, then design challenges that exploit weaknesses. The challenge pool is self-calibrating — too-easy challenges score zero for the author.
- **Agents are just Python packages.** An agent's intelligence is its accumulated source code in `src/agent/`. Evolution modifies these files. The LLM reads them as context for every task.

## Installation and usage

```bash
cd arena
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...

# Bootstrap with LeetCode problems (generates test suites via LLM)
arena bootstrap --easy 5 --medium 5 --hard 3

# Run tournament
arena run --agents 4 --rounds 20 --challenges-per-round 4

# Check status
arena status
```

## Dependencies

- anthropic (API client)
- pyyaml (challenge specs)
- rich (terminal display)
- pytest + hypothesis (test execution)
- requests (LeetCode API)

## Things to know

- `run_tests()` returns 4 values: `(passed, total, error_output, elapsed_seconds)`
- The baseline agent in `baseline/src/agent/core.py` is intentionally naive — every line is meant to be rewritten by evolution
- Seed challenges all have efficiency tests that require O(1) or O(n) solutions
- The `DIRECTIVES` list in `harness.py` rotates authoring themes each round
- Agent evolution can create new files in `src/agent/` — not just modify `core.py`
- The mutator in `mutator.py` injects real utility functions (AST analysis, error classification, etc.) not random garbage
