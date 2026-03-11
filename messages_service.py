from config import CLEAR_MESSAGES
import vk_api


user_messages = {}


def register_message(user_id, message_id):
    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id].append(message_id)


def clear_messages(vk, user_id):

    if not CLEAR_MESSAGES:
        return

    if user_id not in user_messages:
        return

    ids = user_messages[user_id]

    if not ids:
        return

    try:
        vk.messages.delete(
            message_ids=ids,
            delete_for_all=1
        )
    except:
        pass

    user_messages[user_id] = []
