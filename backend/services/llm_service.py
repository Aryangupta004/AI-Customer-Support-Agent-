"""LLM Service using Groq API, with offline fallback (SupportPilot AI)."""
import os
from dotenv import load_dotenv

load_dotenv(override=True)


class LLMService:
    """
    Service for interacting with Groq LLM API.

    If GROQ_API_KEY is missing/invalid, the service runs in OFFLINE mode
    and builds an extractive answer from ticket + KB context instead of
    raising — so the demo UI always works.
    """

    def __init__(self):
        load_dotenv(override=True)

        self.api_key = (os.getenv("GROQ_API_KEY") or "").strip()
        self.model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
        # Treat placeholder values as missing
        if self.api_key and set(self.api_key) == {"x"}:
            self.api_key = ""
        self.offline = not bool(self.api_key)
        self.llm = None

        if not self.offline:
            from langchain_groq import ChatGroq

            print(f"[SupportPilot LLM] Online mode, model: {self.model}")
            self.llm = ChatGroq(
                api_key=self.api_key,
                model_name=self.model,
                temperature=0.3,
                max_tokens=1024,
            )
        else:
            print("[SupportPilot LLM] Offline mode (no GROQ_API_KEY) — using extractive fallback.")

    def generate_response(self, system_prompt: str, user_message: str) -> str:
        """Generate a response from the LLM (or offline fallback)."""
        if self.offline or self.llm is None:
            return self._offline_response(system_prompt, user_message)

        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message),
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"[SupportPilot LLM] API error, falling back offline: {e}")
            return self._offline_response(system_prompt, user_message)

    @staticmethod
    def _offline_response(system_prompt: str, user_message: str) -> str:
        """Extractive fallback: echo the retrieved context in a helpful format."""
        # system_prompt already contains ticket + KB context (see chat_controller)
        return (
            "I'm running in **offline demo mode** (no Groq API key configured), "
            "so here's what I found in the local help-desk data:\n\n"
            f"**Your question:** {user_message}\n\n"
            f"{system_prompt[-2500:]}"
            "\n\n_Add a valid `GROQ_API_KEY` to `.env` and restart the backend "
            "for full AI-generated answers._"
        )

    def generate_response_with_context(
        self,
        system_prompt: str,
        user_message: str,
        kb_context: str = None,
        ticket_context: str = None,
    ) -> str:
        """Generate a response with additional context (KB docs and ticket info)."""
        context_parts = []

        if ticket_context:
            context_parts.append(f"TICKET INFORMATION:\n{ticket_context}\n")

        if kb_context:
            context_parts.append(f"KNOWLEDGE BASE ARTICLES:\n{kb_context}\n")

        enhanced_system_prompt = system_prompt
        if context_parts:
            enhanced_system_prompt += "\n\nCONTEXT TO USE:\n" + "".join(context_parts)

        return self.generate_response(enhanced_system_prompt, user_message)


# Global LLM service instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    # Always create new instance to get latest environment variables
    # (for development/demo purposes)
    return LLMService()
