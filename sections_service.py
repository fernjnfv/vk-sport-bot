import json
from pathlib import Path


DATA_FILE = Path("data/sections.json")


def load_sections():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    return text.strip().lower()


def find_sections(age: int | None, sport: str | None):
    sections = load_sections()
    sport_query = normalize_text(sport) if sport else None

    results = []

    for section in sections:
        age_ok = True
        sport_ok = True

        if age is not None:
            if section["age_to"] is not None and section["age_from"] is not None:
                age_ok = section["age_from"] <= age <= section["age_to"]
            elif section["age_to"] is not None:
                age_ok = age <= section["age_to"]
            elif section["age_from"] is not None:
                age_ok = section["age_from"] <= age

        if sport_query:
            sport_ok = sport_query in normalize_text(section["sport"])

        if age_ok and sport_ok:
            results.append(section)

    return results
