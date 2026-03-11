from typing import Dict, Any

users_data: Dict[int, Dict[str, Any]] = {}


def get_user_state(user_id: int) -> Dict[str, Any]:
    if user_id not in users_data:
        users_data[user_id] = {
            "age": None,
            "sport": None,
            "mode": "main",   # main / waiting_age / waiting_sport / browsing_results
            "results": [],
            "result_index": 0,
            "first_name": "друг",
        }
    return users_data[user_id]
