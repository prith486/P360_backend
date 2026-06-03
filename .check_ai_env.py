from app.core.config import settings
print("AI_PROVIDER=", settings.AI_PROVIDER)
print("OPENAI_KEY_PRESENT=", bool(settings.OPENAI_API_KEY))
print("ANTHROPIC_KEY_PRESENT=", bool(settings.ANTHROPIC_API_KEY))
print("OPENAI_BASE_URL=", settings.OPENAI_BASE_URL)
