"""Thin Anthropic API wrapper with token tracking."""

import os
import threading

import anthropic

DEFAULT_MODEL = os.environ.get("ARENA_MODEL", "claude-haiku-4-5-20251001")


class LLM:
    """Wrapper around Anthropic's API with cumulative token tracking."""

    def __init__(self, model: str | None = None):
        self.client = anthropic.Anthropic()
        self.model = model or DEFAULT_MODEL
        self._input_tokens = 0
        self._output_tokens = 0
        self._lock = threading.Lock()

    def complete(self, system: str, prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Send a completion request. Returns the text response."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        with self._lock:
            self._input_tokens += response.usage.input_tokens
            self._output_tokens += response.usage.output_tokens
        return response.content[0].text

    @property
    def token_usage(self) -> dict[str, int]:
        """Cumulative token usage."""
        with self._lock:
            return {
                "input": self._input_tokens,
                "output": self._output_tokens,
                "total": self._input_tokens + self._output_tokens,
            }

    def reset_usage(self) -> None:
        """Reset token counters."""
        with self._lock:
            self._input_tokens = 0
            self._output_tokens = 0
