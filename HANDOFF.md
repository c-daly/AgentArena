# AgentArena — Handoff Document

## Project Status: MVP functional, needs iteration

The core tournament system is built and working. Agents can solve challenges via Claude Code CLI, author new challenges, evolve their source code, and be subject to random mutations. The pipeline was validated end-to-end: baseline agent solves 9/9 tests on the smart_cache challenge through the claude CLI path.

## Architecture

```
AgentArena/
├── CLAUDE.md              # Project spec (comprehensive)
├── HANDOFF.md             # This file
└── arena/
    ├── pyproject.toml     # pip install -e . → `arena` CLI
    ├── src/arena/
    │   ├── models.py      # Dataclasses: ChallengeSpec, Solution, FitnessReport, AgentInfo, RoundResult, TournamentState
    │   ├── llm.py         # Anthropic API wrapper (thread-safe token tracking). Default model from ARENA_MODEL env var, falls back to claude-haiku-4-5-20251001
    │   ├── agent.py       # Agent runtime: solve/author/evolve. Auto-detects `claude` CLI → uses subscription. Falls back to API. Set ARENA_NO_CLAUDE_CODE=1 to force API.
    │   ├── challenges.py  # run_tests() via pytest subprocess, AST fingerprinting, novelty scoring, challenge I/O
    │   ├── mutator.py     # 6 AST-based mutations, 25% chance per evolve
    │   ├── harness.py     # Tournament class: setup/run/save/load. Parallel solve/author/evolve via ThreadPoolExecutor
    │   ├── display.py     # Rich terminal: live solve grid, phase banners, leaderboard, technique map
    │   ├── leetcode.py    # Fetches LeetCode problems via GraphQL, generates test suites via LLM
    │   └── cli.py         # argparse CLI: arena run, arena bootstrap, arena status
    ├── baseline/src/agent/
    │   ├── __init__.py
    │   └── core.py        # Gen-0 agent: naive solve_prompt, author_prompt, evolve_prompt
    └── seed_challenges/   # 3 challenges with efficiency benchmarks
        ├── 001_smart_cache/
        ├── 002_expression_eval/
        └── 003_schema_validator/
```

## Key Design Decisions

- **Claude Code CLI is the primary runtime**, not the API. The user has a $200/month subscription. The API key (sk-ant-oat01 OAuth token) only has access to Haiku. The `claude` CLI uses the full subscription and can access all models. `agent.py` auto-detects `claude` on PATH.
- **Efficiency is tested, not measured.** Test suites include time-bounded benchmarks. Slow solutions just fail more tests.
- **Full visibility.** After each round, every agent sees every other agent's solutions. This is how innovations propagate.
- **Agents are Python packages.** An agent's intelligence is its `src/agent/core.py`. Evolution rewrites this file. The LLM reads it as context.

## Recent Fixes

### _extract_code was broken (CRITICAL, just fixed)
The `claude` CLI returns responses with preamble text (e.g., `[TRIVIAL]` from user's global CLAUDE.md classification rules) and markdown fences. The old `_extract_code` only stripped fences if they were at the very start of the response. Fixed to use regex to find fenced code blocks anywhere in the response.

### Error output in evolve feedback (just fixed)
Agents now see the last 3 lines of test error output in their fitness report during evolution. Previously they only saw "0/1 (0%)" with no indication of WHY they failed.

### Parallel execution (done)
Solve/author/evolve phases run concurrently via ThreadPoolExecutor (max 8 workers). Rich Live display shows real-time solve grid.

## Known Issues & Next Steps

### The LLM wrapper (llm.py) is only used as API fallback
Since the primary path is Claude Code CLI, `llm.py` is mostly used for:
- leetcode.py bootstrap (generating test suites)
- Token tracking
The default model is Haiku since that's all the OAuth key supports. If the user gets a standard API key, set ARENA_MODEL=claude-opus-4-6.

### User's global CLAUDE.md leaks into agent responses
The `claude` CLI loads `~/.claude/CLAUDE.md` which includes the `[TRIVIAL]`/`[SIMPLE]`/`[COMPLEX]` classification rule. This gets prepended to agent responses. The `_extract_code` regex fix handles this, but ideally agents would run with `--no-user-rules` or a custom system prompt to avoid contamination. Investigate claude CLI flags for this.

### Bootstrap problem with evolution
If all agents start identical and all fail, there's no fitness gradient for evolution to work with. Now that the solve pipeline works (9/9 on smart_cache), this should be less of an issue — agents will produce working solutions, creating real fitness variation.

### Authored challenges need work
The author phase uses a structured text format (TITLE:/DESCRIPTION:/TEST_CODE:/END_CHALLENGE) that's fragile. Consider switching to YAML or JSON output for more reliable parsing.

### Tournament state doesn't persist solution code
Round JSON files save pass/fail stats but not the actual solution code. This means you can't review what agents produced after the fact. Consider saving solution code to disk.

### No git repo yet
The user explicitly deferred git initialization. The project is pushed to https://github.com/c-daly/AgentArena but the tournament working directory (tournament/) is gitignored.

## How to Run

```bash
cd arena
pip install -e .
arena run --agents 4 --rounds 20 --challenges-per-round 3
```

Requires: `claude` CLI on PATH with active subscription, OR ANTHROPIC_API_KEY with ARENA_NO_CLAUDE_CODE=1.

## File Sizes (for context)

| File | Lines | Notes |
|------|-------|-------|
| models.py | ~65 | Stable, unlikely to change |
| llm.py | ~50 | Thread-safe, configurable model |
| agent.py | ~280 | Core runtime, recently fixed _extract_code |
| challenges.py | ~150 | Test execution, AST fingerprinting |
| mutator.py | ~200 | 6 mutation types |
| harness.py | ~370 | Tournament loop, parallel phases |
| display.py | ~280 | Rich live output |
| leetcode.py | ~375 | LeetCode GraphQL + LLM test gen |
| cli.py | ~100 | argparse entry points |
| baseline/core.py | ~80 | Naive prompts, meant to be evolved |
