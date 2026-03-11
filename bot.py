import json
import vk_api

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from config import VK_TOKEN, VK_GROUP_ID, LOGO_ATTACHMENT
from storage import get_user_state
from keyboards import main_keyboard, back_keyboard, results_keyboard
from sections_service import find_sections
from database import create_user, get_user_data, update_name, update_age, update_sport

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)


def send_message(user_id: int, message: str, keyboard=None, attachment=None):
    params = {
        "user_id": user_id,
        "random_id": get_random_id(),
        "message": message,
    }

    if keyboard:
        params["keyboard"] = keyboard

    if attachment:
        params["attachment"] = attachment

    vk.messages.send(**params)

def show_main_menu(user_id: int):
    state = get_user_state(user_id)
    first_name = state.get("first_name", "друг")

    text = (
        f"Привет, {first_name}!\n"
        f"Добро пожаловать в бот поиска спортивных секций.\n\n"
        f"Выбери действие:"
    )

    send_message(
        user_id=user_id,
        message=text,
        keyboard=main_keyboard(age=state["age"], sport=state["sport"]),
        attachment=LOGO_ATTACHMENT
    )


def show_current_result(user_id: int):
    state = get_user_state(user_id)
    results = state["results"]
    index = state["result_index"]

    if not results:
        send_message(
            user_id,
            "Ничего не найдено.",
            keyboard=back_keyboard()
        )
        return

    section = results[index]
    total = len(results)

    text = (
        f"{section['title']}\n\n"
        f"{section['description']}\n\n"
        f"Спорт: {section['sport']}\n"
        f"Возраст: {section['age_from']} - {section['age_to']}\n"
        f"Секция {index + 1} из {total}"
    )

    send_message(
        user_id=user_id,
        message=text,
        keyboard=results_keyboard(
            has_prev=index > 0,
            has_next=index < total - 1
        ),
        attachment=section.get("image_attachment")
    )

def load_from_database(user_id: int):
    user_info = vk.users.get(user_ids=user_id)
    print(1)
    first_name = user_info[0]["first_name"]
    print(2)
    create_user(user_id, first_name)
    user = get_user_data(user_id)
    state = get_user_state(user_id)
    state["first_name"] = user["first_name"]
    state["age"] = user["age"]
    state["sport"] = user["sport"]
    state["loaded_from_database"] = True

def handle_new_message(event):
    user_id = event.obj.message["from_id"]
    text = event.obj.message.get("text", "").strip()
    state = get_user_state(user_id)
    user_info = vk.users.get(user_ids=user_id)
    # Получаем имя пользователя, если ещё не сохраняли
    if not state["loaded_from_database"]:
        print("пытаюсь загрузиться из БД")
        load_from_database(user_id)
        print("загрузка из БД завершена")
    if user_info[0]["first_name"] != state["first_name"]:
        state["first_name"] = user_info[0]["first_name"]
        print("обновляю имя в БД")
        update_name(user_id, state["first_name"])

    if text.lower() in ["start", "начать", "привет", "hello"]:
        state["mode"] = "main"
        show_main_menu(user_id)
        return

    if state["mode"] == "waiting_age":
        if text.isdigit():
            state["age"] = int(text)
            update_age(user_id, state["age"])
            state["mode"] = "main"
            show_main_menu(user_id)
        else:
            send_message(
                user_id,
                "Пожалуйста, введи возраст числом. Например: 12",
                keyboard=back_keyboard()
            )
        return

    if state["mode"] == "waiting_sport":
        if text:
            state["sport"] = text
            update_sport(user_id, state["sport"])
            state["mode"] = "main"
            show_main_menu(user_id)
        else:
            send_message(
                user_id,
                "Пожалуйста, введи вид спорта.",
                keyboard=back_keyboard()
            )
        return

    show_main_menu(user_id)


def handle_callback(event):
    print(event.obj)

    user_id = event.obj.user_id
    payload = event.obj.payload
    cmd = payload.get("cmd")

    state = get_user_state(user_id)
    if not state["loaded_from_database"]:
        load_from_database(user_id)
    # Обязательный ответ на callback
    vk.messages.send_message_event_answer(
        event_id=event.obj.event_id,
        user_id=user_id,
        peer_id=event.obj.peer_id
    )

    if cmd == "set_age":
        state["mode"] = "waiting_age"
        send_message(
            user_id,
            "Введи возраст числом:",
            keyboard=back_keyboard()
        )
        return

    if cmd == "set_sport":
        state["mode"] = "waiting_sport"
        send_message(
            user_id,
            "Введи вид спорта или его часть:",
            keyboard=back_keyboard()
        )
        return

    if cmd == "find_sections":
        results = find_sections(age=state["age"], sport=state["sport"])
        state["results"] = results
        state["result_index"] = 0
        state["mode"] = "browsing_results"

        if not results:
            send_message(
                user_id,
                "По вашему запросу ничего не найдено.",
                keyboard=back_keyboard()
            )
        else:
            show_current_result(user_id)
        return

    if cmd == "prev_result":
        if state["result_index"] > 0:
            state["result_index"] -= 1
        show_current_result(user_id)
        return

    if cmd == "next_result":
        if state["result_index"] < len(state["results"]) - 1:
            state["result_index"] += 1
        show_current_result(user_id)
        return

    if cmd == "back_to_main":
        state["mode"] = "main"
        show_main_menu(user_id)
        return


def main():
    print("Бот запущен...")

    for event in longpoll.listen():
        try:
            if event.type == VkBotEventType.MESSAGE_NEW:
                print("MESSAGE_NEW")
                handle_new_message(event)

            elif event.type == VkBotEventType.MESSAGE_EVENT:
                print("MESSAGE_EVENT")
                handle_callback(event)

        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
