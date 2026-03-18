"""Thin Anthropic API wrapper with token tracking."""

import anthropic


class LLM:
    """Wrapper around Anthropic's API with cumulative token tracking."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY from env
        self.model = model
        self._input_tokens = 0
        self._output_tokens = 0

    def complete(self, system: str, prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Send a completion request. Returns the text response."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        self._input_tokens += response.usage.input_tokens
        self._output_tokens += response.usage.output_tokens
        return response.content[0].text

    @property
    def token_usage(self) -> dict[str, int]:
        """Cumulative token usage."""
        return {
            "input": self._input_tokens,
            "output": self._output_tokens,
            "total": self._input_tokens + self._output_tokens,
        }

    def reset_usage(self) -> None:
        """Reset token counters."""
        self._input_tokens = 0
        self._output_tokens = 0
