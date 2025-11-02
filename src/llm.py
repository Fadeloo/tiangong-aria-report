"""LLM client abstractions and helpers for multi-model writing."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol
from urllib import error, request

LOGGER = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Exception raised when an LLM call cannot be completed."""


@dataclass
class LLMClientConfig:
    """Configuration block describing how to reach a chat-completion model."""

    identifier: str
    model: str
    provider: str = "openai-compatible"
    api_key_env: str = "OPENAI_API_KEY"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 60.0
    extra_headers: Dict[str, str] = field(default_factory=dict)

    def resolve_api_key(self) -> str:
        """Return the API key, preferring explicit value over environment."""

        if self.api_key:
            return self.api_key
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise LLMError(
                f"Missing API key for LLM client '{self.identifier}'. "
                f"Provide it via parameter or environment variable '{self.api_key_env}'."
            )
        return api_key


@dataclass
class LLMGenerationPrompt:
    """Container for system and user messages sent to an LLM."""

    system_prompt: str
    user_prompt: str
    temperature: float = 0.3
    max_output_tokens: int = 800
    top_p: float = 0.9


@dataclass
class LLMGeneration:
    """Normalized representation of a model response."""

    text: str
    model: str
    provider: str
    raw: Dict[str, object] = field(default_factory=dict)


class LLMClient(Protocol):
    """Protocol describing the minimum surface for an LLM chat client."""

    identifier: str
    model: str
    provider: str

    def generate(self, prompt: LLMGenerationPrompt) -> LLMGeneration:
        """Return a generation for the supplied prompt."""


class OpenAICompatibleClient:
    """Thin wrapper for OpenAI's chat completion API and compatible providers."""

    def __init__(self, config: LLMClientConfig) -> None:
        if config.provider not in {"openai", "openai-compatible"}:
            raise LLMError(
                f"OpenAICompatibleClient only supports provider 'openai' or 'openai-compatible', got '{config.provider}'."
            )
        self.identifier = config.identifier
        self.model = config.model
        self.provider = config.provider
        self._api_key = config.resolve_api_key()
        self._base_url = (config.base_url or "https://api.openai.com").rstrip("/")
        self._timeout = config.timeout
        self._extra_headers = config.extra_headers

    def generate(self, prompt: LLMGenerationPrompt) -> LLMGeneration:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt.system_prompt},
                {"role": "user", "content": prompt.user_prompt},
            ],
            "temperature": prompt.temperature,
            "max_tokens": prompt.max_output_tokens,
            "top_p": prompt.top_p,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
            **self._extra_headers,
        }
        url = f"{self._base_url}/v1/chat/completions"
        req = request.Request(url, data=body, headers=headers, method="POST")

        try:
            with request.urlopen(req, timeout=self._timeout) as response:
                response_bytes = response.read()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            LOGGER.error(
                "HTTP error from LLM provider %s (%s): %s", self.provider, self.identifier, detail
            )
            raise LLMError(f"LLM request failed with status {exc.code}: {detail}") from exc
        except error.URLError as exc:
            LOGGER.error("Network error contacting LLM provider %s: %s", self.identifier, exc)
            raise LLMError(f"Failed to reach LLM provider {self.identifier}: {exc}") from exc

        try:
            parsed = json.loads(response_bytes.decode("utf-8"))
            content = parsed["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            LOGGER.error("Unexpected payload when calling LLM %s: %s", self.identifier, response_bytes)
            raise LLMError("Unable to parse LLM response payload") from exc

        return LLMGeneration(text=content, model=self.model, provider=self.provider, raw=parsed)