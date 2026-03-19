from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


Message = Dict[str, str]


@dataclass
class ChatPrompt:
    messages: List[Message]


class LLMClient(Protocol):
    async def chat(self, prompt: ChatPrompt, **kwargs: Any) -> Dict[str, Any]:
        """
        Returns a dict with "content" (str) and "usage" (dict with "prompt_tokens" and "completion_tokens").
        """
        ...
