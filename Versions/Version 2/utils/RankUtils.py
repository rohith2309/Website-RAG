POSITIVE_KEYWORDS = [
    "features",
    "specifications",
    "specs",
    "models",
    "product",
    "technology",
    "safety",
    "faq",
]

NEGATIVE_KEYWORDS = [
    "login",
    "signup",
    "contact",
    "dealer",
    "callback",
    "test-drive",
    "booking",
    "privacy",
    "terms",
]


def score_url(url: str) -> int:
    url = url.lower()

    score = 0

    for keyword in POSITIVE_KEYWORDS:
        if keyword in url:
            score += 1

    for keyword in NEGATIVE_KEYWORDS:
        if keyword in url:
            score -= 1

    return score