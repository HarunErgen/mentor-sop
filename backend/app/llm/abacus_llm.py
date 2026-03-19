import os
from abacusai import ApiClient
from typing import Any, Dict, List, Protocol

import anyio

from app.llm.llm_client import ChatPrompt

class AbacusLLMClient:
    def __init__(self) -> None:
        api_key = os.getenv("ABACUS_API_KEY")
        if not api_key:
            raise RuntimeError("ABACUS_API_KEY environment variable is not set.")
        self._client = ApiClient(api_key)
        self._llm_name = os.getenv("ABACUS_DEFAULT_LLM")

    async def chat(self, prompt: ChatPrompt, **kwargs: Any) -> Dict[str, Any]:
        system_message = ""
        user_parts: List[str] = []

        for msg in prompt.messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system" and not system_message:
                system_message = content
            else:
                user_parts.append(f"[{role.upper()}] {content}")

        user_prompt = "\n\n".join(user_parts)

        def _call_sync() -> Any:
            return self._client.evaluate_prompt(
                prompt=user_prompt,
                system_message=system_message or None,
                llm_name=self._llm_name,
            )

        response = await anyio.to_thread.run_sync(_call_sync)
        
        content = getattr(response, "content", str(response))
        
        # Try to extract usage from Abacus response
        prompt_tokens = getattr(response, "prompt_tokens", 0)
        completion_tokens = getattr(response, "completion_tokens", 0)
        
        # Fallback estimation if tokens are not provided (1 token per 4 chars)
        if prompt_tokens == 0:
            prompt_tokens = (len(user_prompt) + len(system_message)) // 4
        if completion_tokens == 0:
            completion_tokens = len(content) // 4
            
        return {
            "content": content,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }

abacus_llm_client = AbacusLLMClient()
