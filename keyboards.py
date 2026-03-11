import json
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def main_keyboard(age=None, sport=None):
    keyboard = VkKeyboard(inline=True)

    age_text = f"Возраст: {age}" if age is not None else "Возраст: не указан"
    sport_text = f"Спорт: {sport}" if sport else "Спорт: не указан"

    keyboard.add_callback_button(
        label=age_text,
        color=VkKeyboardColor.PRIMARY,
        payload=json.dumps({"cmd": "set_age"})
    )
    keyboard.add_line()

    keyboard.add_callback_button(
        label=sport_text,
        color=VkKeyboardColor.PRIMARY,
        payload=json.dumps({"cmd": "set_sport"})
    )
    keyboard.add_line()

    keyboard.add_callback_button(
        label="Найти секции",
        color=VkKeyboardColor.POSITIVE,
        payload=json.dumps({"cmd": "find_sections"})
    )

    return keyboard.get_keyboard()


def back_keyboard():
    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(
        label="Назад",
        color=VkKeyboardColor.SECONDARY,
        payload=json.dumps({"cmd": "back_to_main"})
    )
    return keyboard.get_keyboard()


def results_keyboard(index: int, total: int, has_prev: bool, has_next: bool):
    keyboard = VkKeyboard(inline=True)

    if has_prev:
        keyboard.add_callback_button(
            label="⬅️",
            color=VkKeyboardColor.PRIMARY,
            payload={"cmd": "prev_result"}
        )
    else:
        keyboard.add_callback_button(
            label="·",
            color=VkKeyboardColor.SECONDARY,
            payload={"cmd": "ignore"}
        )

    keyboard.add_callback_button(
        label=f"{index + 1} / {total}",
        color=VkKeyboardColor.SECONDARY,
        payload={"cmd": "ignore"}
    )

    if has_next:
        keyboard.add_callback_button(
            label="➡️",
            color=VkKeyboardColor.PRIMARY,
            payload={"cmd": "next_result"}
        )
    else:
        keyboard.add_callback_button(
            label="·",
            color=VkKeyboardColor.SECONDARY,
            payload={"cmd": "ignore"}
        )

    keyboard.add_line()

    keyboard.add_callback_button(
        label="🏠 В меню",
        color=VkKeyboardColor.SECONDARY,
        payload={"cmd": "back_to_main"}
    )

    return keyboard.get_keyboard()

def sports_keyboard(sports: list[str], page: int, per_page: int = 6):
    keyboard = VkKeyboard(inline=True)

    total_pages = (len(sports) + per_page - 1) // per_page
    start = page * per_page
    end = start + per_page
    page_items = sports[start:end]

    for i in range(0, len(page_items), 2):
        keyboard.add_callback_button(
            label=page_items[i],
            color=VkKeyboardColor.PRIMARY,
            payload={"cmd": "choose_sport", "sport": page_items[i]}
        )

        if i + 1 < len(page_items):
            keyboard.add_callback_button(
                label=page_items[i + 1],
                color=VkKeyboardColor.PRIMARY,
                payload={"cmd": "choose_sport", "sport": page_items[i + 1]}
            )

        if i + 2 < len(page_items):
            keyboard.add_line()

    keyboard.add_line()

    has_prev = page > 0
    has_next = page < total_pages - 1

    if has_prev:
        keyboard.add_callback_button(
            label="⬅️",
            color=VkKeyboardColor.SECONDARY,
            payload={"cmd": "sports_prev", "page": page - 1}
        )
    else:
        keyboard.add_callback_button(
            label="·",
            color=VkKeyboardColor.SECONDARY,
            payload={"cmd": "ignore"}
        )

    keyboard.add_callback_button(
        label=f"{page + 1} / {total_pages}",
        color=VkKeyboardColor.SECONDARY,
        payload={"cmd": "ignore"}
    )

    if has_next:
        keyboard.add_callback_button(
            label="➡️",
            color=VkKeyboardColor.SECONDARY,
            payload={"cmd": "sports_next", "page": page + 1}
        )
    else:
        keyboard.add_callback_button(
            label="·",
            color=VkKeyboardColor.SECONDARY,
            payload={"cmd": "ignore"}
        )

    keyboard.add_line()
    keyboard.add_callback_button(
        label="🏠 В меню",
        color=VkKeyboardColor.SECONDARY,
        payload={"cmd": "back_to_main"}
    )

    return keyboard.get_keyboard()

def sport_mode_keyboard():
    keyboard = VkKeyboard(inline=True)

    keyboard.add_callback_button(
        label="✍️ Ввести спорт",
        color=VkKeyboardColor.PRIMARY,
        payload={"cmd": "sport_input_mode"}
    )
    keyboard.add_line()

    keyboard.add_callback_button(
        label="📚 Выбрать из списка",
        color=VkKeyboardColor.PRIMARY,
        payload={"cmd": "sport_list_mode", "page": 0}
    )
    keyboard.add_line()

    keyboard.add_callback_button(
        label="🏠 На главную",
        color=VkKeyboardColor.SECONDARY,
        payload={"cmd": "back_to_main"}
    )

    return keyboard.get_keyboard()