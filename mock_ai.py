import random
import re

TEMPLATES = {
    "Friendly": {
        "high": [
            "Had such a great time at {store}! {Highlights}. Everyone was so welcoming, and I'll definitely be back soon!",
            "Loved my visit to {store}. {Highlights}. It's a lovely spot and I'd happily recommend it to friends.",
        ],
        "mid": [
            "Decent visit to {store}. {Highlights}. A few things could be better, but I'd give it another try.",
        ],
        "low": [
            "My visit to {store} wasn't the best. {Highlights}. I hope the team can improve things for next time.",
        ],
    },
    "Professional": {
        "high": [
            "I had an excellent experience at {store}. {Highlights}. The quality and service were consistently strong, and I recommend them.",
            "{store} delivered a very satisfying experience. {Highlights}. I would not hesitate to return.",
        ],
        "mid": [
            "My experience at {store} was acceptable overall. {Highlights}. There is some room for improvement.",
        ],
        "low": [
            "My experience at {store} fell short of expectations. {Highlights}. I hope management will address these concerns.",
        ],
    },
    "Concise": {
        "high": ["Great experience at {store}. {Highlights}. Highly recommend."],
        "mid": ["Okay experience at {store}. {Highlights}."],
        "low": ["Disappointing visit to {store}. {Highlights}."],
    },
}


def _highlights(notes: str) -> str:
    parts = [p.strip(" -*\t") for p in re.split(r"[,\n;•]+", notes)]
    parts = [p for p in parts if p]
    if not parts:
        return "Overall a solid experience"
    if len(parts) == 1:
        text = parts[0]
    else:
        text = ", ".join(parts[:-1]) + " and " + parts[-1]
    return text[0].upper() + text[1:]


def mock_review(store: str, rating: int, notes: str, tone: str) -> str:
    bucket = "high" if rating >= 4 else "mid" if rating == 3 else "low"
    options = TEMPLATES.get(tone, TEMPLATES["Friendly"])[bucket]
    return random.choice(options).format(
        store=store or "this place", Highlights=_highlights(notes)
    )
