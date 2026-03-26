import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def categorize_text_answers(question_text: str, answers: list[str]) -> list[dict]:
    """
    AI yordamida matnli javoblarni asosiy kategoriyalarga ajratadi.
    Qaytaradi: [{'category': '...', 'count': N, 'percent': X.X, 'examples': [...]}]
    """
    if not answers:
        return []

    answers_numbered = "\n".join(f"{i+1}. {a}" for i, a in enumerate(answers) if a and a.strip())
    if not answers_numbered:
        return []

    prompt = f"""Quyidagi so'rovnoma savoli uchun foydalanuvchilar tomonidan berilgan matnli javoblarni tahlil qiling.

Savol: {question_text}

Javoblar:
{answers_numbered}

Vazifa: Ushbu javoblarni mantiqiy toifalarga ajrating.
- 3 dan 6 gacha toifa aniqlang
- Har bir toifaga qancha javob kirishi va foizini hisoblang
- Har bir toifadan 1-2 ta namunaviy javob ko'rsating

Javobni FAQAT JSON formatida bering (boshqa matn yo'q):
[
  {{
    "category": "Toifa nomi (o'zbekcha)",
    "count": N,
    "percent": X.X,
    "examples": ["misol 1", "misol 2"]
  }}
]"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # JSON blokdan tozalash
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        print(f"AI kategoriyalashtirish xatosi: {e}")
        return []
