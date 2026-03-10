"""
Telegram bot: free-form user request -> LLM (function calling) extracts filters
-> query DB -> readable response.
"""
import json
import logging
from openai import OpenAI

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from config import settings
from db import query_cars

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

OPENAI_CLIENT = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

# Function schema for LLM to extract car search params
SEARCH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_cars",
            "description": "Search car ads by make, model, color, year range, or price range. Use this when the user asks to find, search, or list cars with any criteria.",
            "parameters": {
                "type": "object",
                "properties": {
                    "make": {
                        "type": "string",
                        "description": "Car make/brand (e.g. BMW, Toyota, Honda)",
                    },
                    "model": {
                        "type": "string",
                        "description": "Model name or part of it",
                    },
                    "color": {
                        "type": "string",
                        "description": "Exterior color (e.g. red, black, white)",
                    },
                    "year_min": {
                        "type": "integer",
                        "description": "Minimum year (e.g. 2020)",
                    },
                    "year_max": {
                        "type": "integer",
                        "description": "Maximum year",
                    },
                    "price_max": {
                        "type": "integer",
                        "description": "Maximum price in yen (e.g. 2000000 for 2 million)",
                    },
                    "price_min": {
                        "type": "integer",
                        "description": "Minimum price in yen",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max number of results (default 10, max 20)",
                    },
                },
            },
        },
    }
]


def extract_params_with_llm(user_text: str) -> dict | None:
    """Use OpenAI to extract search parameters from free-form text. Returns None if no LLM or no tool call."""
    if not OPENAI_CLIENT:
        return None
    try:
        resp = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You extract car search parameters from the user's message. Call the search_cars function with the extracted parameters. Price in yen: 1 million = 1000000, 2 million = 2000000. If the user says 'up to 2 million' set price_max to 2000000. If no relevant params, still call search_cars with empty params to return recent listings.",
                },
                {"role": "user", "content": user_text},
            ],
            tools=SEARCH_TOOLS,
            tool_choice="auto",
        )
        choice = resp.choices[0]
        if not choice.message.tool_calls:
            return {}
        for tc in choice.message.tool_calls:
            if tc.function.name == "search_cars":
                args = json.loads(tc.function.arguments or "{}")
                limit = args.get("limit")
                if limit is None:
                    args["limit"] = 10
                else:
                    args["limit"] = min(20, max(1, int(limit)))
                return args
        return {}
    except Exception as e:
        logger.exception("LLM extraction failed: %s", e)
        return None


def format_cars_reply(cars: list[dict]) -> str:
    if not cars:
        return "No cars found matching your criteria."
    lines = []
    for i, c in enumerate(cars, 1):
        make = c.get("make") or "—"
        model = c.get("model") or "—"
        year = c.get("year") or "—"
        price = c.get("price")
        price_str = f"{price / 10_000:.1f}万" if price is not None else "—"
        color = c.get("color") or "—"
        link = c.get("link") or ""
        lines.append(f"{i}. {make} {model} | {year} | {price_str} | {color}\n   {link}")
    return "\n".join(lines)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message and update.message.text) or ""
    if not text.strip():
        await update.message.reply_text("Send me a request like: «Find a red BMW up to 2 million» and I'll search car ads for you.")
        return

    params = extract_params_with_llm(text)
    if params is None:
        await update.message.reply_text(
            "Search is temporarily unavailable (LLM not configured). "
            "Please set OPENAI_API_KEY in .env. If you don't have a key, contact the team."
        )
        return

    cars = query_cars(
        make=params.get("make"),
        model=params.get("model"),
        color=params.get("color"),
        year_min=params.get("year_min"),
        year_max=params.get("year_max"),
        price_max=params.get("price_max"),
        price_min=params.get("price_min"),
        limit=params.get("limit", 10),
    )
    reply = format_cars_reply(cars)
    await update.message.reply_text(reply[:4000] or "No results.")


def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        return
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot running")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
