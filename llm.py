import json
from pathlib import Path
import config

_CANNED = Path(__file__).parent / "fixtures" / "llm_responses.json"


def build_prompt(app):
    return (
        "You are triaging a startup application for a VC fund. For each criterion in "
        f"{config.CRITERIA}, return a verdict (match | partial | no-match | insufficient-data) "
        "and a short citation quoted from the application or deck. Use insufficient-data "
        "when the material does not establish the criterion; do not guess.\n"
        'Reply with JSON only: {"criteria": {"<criterion>": {"verdict": "...", "citation": "..."}}, '
        '"tokens_in": <int>, "tokens_out": <int>}\n\n'
        f"Application: {app['name']}\nStage: {app['stage']}\nSector: {app['sector']}\n"
        f"HQ: {app['hq']}\nFounders: {app['founders']}\nModel: {app['model']}\n"
        f"Round size (INR cr): {app['round_size_cr']}\n\nDeck:\n{app['deck']}"
    )


def assess(app_id, prompt):
    """Return the model's per-criterion verdicts and token counts for one application."""
    if config.OFFLINE:
        return json.loads(_CANNED.read_text())[app_id]

    from google import genai
    client = genai.Client(api_key=config.API_KEY)
    resp = client.models.generate_content(
        model=config.MODEL, contents=prompt, config={"temperature": config.TEMPERATURE})
    return json.loads(resp.text)
