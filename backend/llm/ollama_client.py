import httpx
import logging
from typing import Optional
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.1-8b-instant"  # free tier, fast

FRAUD_ANALYST_SYSTEM = """You are an expert UPI fraud analyst AI assistant.
You help analysts investigate suspicious transactions and fraud cases.
Always be concise, factual, and specific. Base your analysis on the data provided.
When explaining fraud signals, cite the specific features and their values.
Format your response clearly with short paragraphs.
Never make up information not present in the context."""


async def check_ollama() -> bool:
    return bool(config.GROQ_API_KEY)


async def get_available_models() -> list:
    return [GROQ_MODEL]


async def generate(prompt: str,
                   system: Optional[str] = None,
                   model: Optional[str]  = None,
                   temperature: float    = 0.1,
                   max_tokens: int       = 400) -> str:
    if not config.GROQ_API_KEY:
        return "Groq API key not configured. Add GROQ_API_KEY to .env file."

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model":       model or GROQ_MODEL,
        "messages":    messages,
        "temperature": temperature,
        "max_tokens":  max_tokens
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                GROQ_API_URL,
                json    = payload,
                headers = {
                    "Authorization": f"Bearer {config.GROQ_API_KEY}",
                    "Content-Type":  "application/json"
                }
            )
            if r.status_code != 200:
                logger.error(f"Groq error {r.status_code}: {r.text}")
                return f"LLM error: {r.status_code}"

            data = r.json()
            return data['choices'][0]['message']['content'].strip()

    except httpx.TimeoutException:
        return "LLM request timed out."
    except Exception as e:
        logger.error(f"Groq generate failed: {e}")
        return f"LLM error: {str(e)}"