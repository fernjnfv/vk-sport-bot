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

