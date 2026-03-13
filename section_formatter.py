
SPORT_ICONS = {
    "футбол": "⚽",
    "баскетбол": "🏀",
    "волейбол": "🏐",
    "хоккей": "🏒",
    "плавание": "🏊",
    "гимнастика": "🤸",
    "акробатика": "🤸",
    "экстрим": "🛹",
    "ролики": "🛼",
    "горные лыжи": "⛷️",
    "картинг": "🏎️",
    "гребля": "🚣",
}

def format_section_card(section, index=None, total=None):

    sport = section.get("sport", "")
    icon = SPORT_ICONS.get(sport, "🏅")

    lines = [f"{icon} {section['title']}", ""]

    # описание
    if section.get("description"):
        lines.append(section["description"])
        lines.append("")

    # возраст
    age_from = section.get("age_from")
    age_to = section.get("age_to")

    if age_from or age_to:
        if age_from and age_to:
            lines.append(f"👶 Возраст: {age_from}-{age_to} лет")
        elif age_from:
            lines.append(f"👶 Возраст: от {age_from} лет")
        elif age_to:
            lines.append(f"👶 Возраст: до {age_to} лет")

    # тренер
    if section.get("trainer"):
        lines.append(f"👨‍🏫 Тренер: {section['trainer']}")

    # телефон
    if section.get("phone"):
        lines.append(f"📞 Телефон: {section['phone']}")

    # ссылка
    if section.get("vk"):
        lines.append("🔗 Группа VK:")
        lines.append(section["vk"])

    # номер секции
    if index is not None and total is not None:
        lines.append("")
        lines.append(f"Секция {index + 1} / {total}")

    return "\n".join(lines)


