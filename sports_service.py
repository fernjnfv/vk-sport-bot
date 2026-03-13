
def get_unique_sports(sections):
    sports = set()

    for s in sections:
        sports.add(s["sport"])

    return sorted(list(sports))
