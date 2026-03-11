from sections_service import load_sections

def get_unique_sports():
    sections = load_sections()
    sports = set()

    for s in sections:
        sports.add(s["sport"])

    return sorted(list(sports))
