import vk_api
from messages_service import register_message, clear_messages
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from sports_service import get_unique_sports

from config import VK_TOKEN, VK_GROUP_ID, LOGO_ATTACHMENT
from storage import get_user_state
from keyboards import main_keyboard, back_keyboard, results_keyboard, sport_mode_keyboard, sports_keyboard
from sections_service import find_sections
from database import create_user, get_user_data, update_name, update_age, update_sport, update_last_bot_message, get_last_bot_message

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)
all_sports = get_unique_sports()

def render_screen(user_id: int, peer_id: int, message: str, keyboard=None, attachment=None):
    last_message_id, last_peer_id = get_last_bot_message(user_id)

    params = {
        "peer_id": peer_id,
        "message": message,
    }

    if keyboard:
        params["keyboard"] = keyboard

    if attachment:
        params["attachment"] = attachment

    # 1. Пробуем редактировать последнее сообщение бота
    if last_message_id and last_peer_id == peer_id:
        try:
            vk.messages.edit(
                message_id=last_message_id,
                peer_id=peer_id,
                message=message,
                keyboard=keyboard,
                attachment=attachment
            )
            print(f"удачно измениел сообщение")
            return last_message_id
        except Exception:
            print(f"Не удалось отредактировать сообщение: {e}")
            pass

    # 2. Если не получилось — отправляем новое
    sent_message_id = vk.messages.send(
        peer_id=peer_id,
        random_id=get_random_id(),
        message=message,
        keyboard=keyboard,
        attachment=attachment
    )

    update_last_bot_message(user_id, sent_message_id, peer_id)
    return sent_message_id

def delete_user_message(event):
    try:
        print(f"пытаюсь удалить польз сообщ")
        msg = event.obj.message
        message_id = msg.get("id")
        cmid = msg.get("conversation_message_id")
        peer_id = msg.get("peer_id")

        # Сначала пробуем по обычному id
        if message_id:
            try:
                vk.messages.delete(
                    message_ids=message_id,
                    delete_for_all=1
                )
                return
            except Exception:
                pass

        # Если не вышло — пробуем по conversation_message_id
        if cmid and peer_id:
            try:
                vk.messages.delete(
                    cmids=cmid,
                    peer_id=peer_id,
                    delete_for_all=1
                )
                return
            except Exception:
                pass

    except Exception:
        pass

def send_message_old(user_id, message, keyboard=None, attachment=None):

    clear_messages(vk, user_id)

    params = {
        "user_id": user_id,
        "random_id": get_random_id(),
        "message": message
    }

    if keyboard:
        params["keyboard"] = keyboard

    if attachment:
        params["attachment"] = attachment

    response = vk.messages.send(**params)

    register_message(user_id, response)


def show_main_menu(user_id: int, peer_id: int):
    state = get_user_state(user_id)
    first_name = state.get("first_name", "друг")

    text = (
        f"Привет, {first_name}!\n"
        f"Добро пожаловать в бот поиска спортивных секций.\n\n"
        f"Выбери действие:"
    )

    render_screen(
        user_id=user_id,
        peer_id=peer_id,
        message=text,
        keyboard=main_keyboard(age=state["age"], sport=state["sport"]),
        attachment=LOGO_ATTACHMENT
    )


def show_current_result(user_id: int, peer_id: int):
    state = get_user_state(user_id)
    results = state["results"]
    index = state["result_index"]

    if not results:
        render_screen(
            user_id,
            peer_id=peer_id,
            message="Ничего не найдено.",
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
    )

    render_screen(
        user_id=user_id,
        peer_id=peer_id,
        message=text,
        keyboard=results_keyboard(
            index=index,
            total=total,
            has_prev=index > 0,
            has_next=index < total - 1,
        ),
        attachment=section.get("image_attachment")
    )

def load_from_database(user_id: int):
    user_info = vk.users.get(user_ids=user_id)
    first_name = user_info[0]["first_name"]
    create_user(user_id, first_name)
    user = get_user_data(user_id)
    state = get_user_state(user_id)
    state["first_name"] = user["name"]
    state["age"] = user["age"]
    state["sport"] = user["sport"]
    state["loaded_from_database"] = True

def handle_new_message(event):
    msg = event.obj.message
    user_id = msg["from_id"]
    peer_id = msg["peer_id"]
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

    handled = False
    if text.lower() in ["start", "начать", "привет", "hello"]:
        state["mode"] = "main"
        show_main_menu(user_id, peer_id)
        handled = True

    elif state["mode"] == "waiting_age":
        if text.isdigit():
            state["age"] = int(text)
            update_age(user_id, state["age"])
            state["mode"] = "main"
            show_main_menu(user_id,peer_id)
        else:
            render_screen(
                user_id,
                peer_id=peer_id,
                message="Пожалуйста, введи возраст числом. Например: 12",
                keyboard=back_keyboard()
            )
        handled = True

    elif state["mode"] == "waiting_sport":
        if text:
            state["sport"] = text
            update_sport(user_id, state["sport"])
            state["mode"] = "main"
            show_main_menu(user_id,peer_id)
        else:
            render_screen(
                user_id,
                peer_id=peer_id,
                message="Пожалуйста, введи вид спорта.",
                keyboard=back_keyboard()
            )
        handled = True
    else:
        show_main_menu(user_id, peer_id)
        handled = True
    if handled:
        delete_user_message(event)

def handle_callback(event):
    print(event.obj)
    peer_id = event.obj.peer_id
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
        peer_id=peer_id
    )
    if cmd == "ignore":
        return

    if cmd == "set_age":
        state["mode"] = "waiting_age"
        render_screen(
            user_id,
            peer_id = peer_id,
            message="Введи возраст числом:",
            keyboard=back_keyboard()
        )
        return

    if cmd == "set_sport":
        state["mode"] = "choose_sport_mode"
        render_screen(
            user_id,
            peer_id=peer_id,
            message="Выбери, как указать спорт:",
            keyboard=sport_mode_keyboard()
        )
        return

    if cmd == "sport_input_mode":
        state["mode"] = "waiting_sport"
        render_screen(
            user_id,
            peer_id=peer_id,
            message="Введи вид спорта или его часть:",
            keyboard=back_keyboard()
        )
        return

    if cmd == "sport_list_mode":
        page = payload.get("page", 0)
        state["mode"] = "choosing_sport_from_list"
        render_screen(
            user_id,
            peer_id=peer_id,
            message="Выбери вид спорта из списка:",
            keyboard=sports_keyboard(sports=all_sports, page=page)
        )
        return

    if cmd == "sports_prev":
        page = payload.get("page", 0)
        state["mode"] = "choosing_sport_from_list"
        render_screen(
            user_id,
            peer_id=peer_id,
            message="Выбери вид спорта из списка:",
            keyboard=sports_keyboard(sports=all_sports, page=page)
        )
        return

    if cmd == "sports_next":
        page = payload.get("page", 0)
        state["mode"] = "choosing_sport_from_list"
        render_screen(
            user_id,
            peer_id=peer_id,
            message="Выбери вид спорта из списка:",
            keyboard=sports_keyboard(sports=all_sports, page=page)
        )
        return
    if cmd == "choose_sport":
        sport = payload.get("sport")
        if sport:
            state["sport"] = sport
            update_sport(user_id, state["sport"])
            state["mode"] = "main"
            show_main_menu(user_id, peer_id)
        return

    if cmd == "find_sections":
        results = find_sections(age=state["age"], sport=state["sport"])
        state["results"] = results
        state["result_index"] = 0
        state["mode"] = "browsing_results"

        if not results:
            render_screen(
                user_id,
                peer_id=peer_id,
                message="По вашему запросу ничего не найдено.",
                keyboard=back_keyboard()
            )
        else:
            show_current_result(user_id, peer_id)
        return

    if cmd == "prev_result":
        if state["result_index"] > 0:
            state["result_index"] -= 1
        show_current_result(user_id, peer_id)
        return

    if cmd == "next_result":
        if state["result_index"] < len(state["results"]) - 1:
            state["result_index"] += 1
        show_current_result(user_id, peer_id)
        return

    if cmd == "back_to_main":
        state["mode"] = "main"
        show_main_menu(user_id, peer_id)
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
