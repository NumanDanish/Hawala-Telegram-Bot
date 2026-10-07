import os
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.5-flash-lite"


class HawalaRequest(BaseModel):
    amount: Optional[float]
    currency: Optional[str]
    sender: Optional[str]
    receiver: Optional[str]
    city: Optional[str]
    receiver_phone: Optional[str]


class HawalaBatch(BaseModel):
    transfers: list[HawalaRequest]


SYSTEM_PROMPT = """You extract Hawala transfer details from customer messages.
Messages may be in English, Pashto, Dari, or mixed.
Only use information written in the message.
If a detail is missing, leave it empty (null). Never guess.
If the currency is not written, leave it empty. Do not assume USD.
Write currency as a 3-letter code, like USD, AFN, PKR.
A message may contain more than one transfer. Extract each one separately.
If the message is not a transfer request, return an empty list."""


async def extract(message: str) -> list[HawalaRequest]:
    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=HawalaBatch,
        ),
    )
    data = response.parsed
    if data is None:
        return []
    return data.transfers