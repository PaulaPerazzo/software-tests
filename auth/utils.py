import datetime
from fastapi import HTTPException

login_attempts = {}

MAX_ATTEMPTS = 3
BLOCK_DURATION = datetime.timedelta(minutes=5)

def check_user_block(username: str) -> bool:
    user_data = login_attempts.get(username)
    
    if user_data and user_data.get("blocked_until"):
        if datetime.datetime.now() < user_data["blocked_until"]:
            return True
        else:
            reset_attempts(username)
    
    return False

def record_failed_attempt(username: str) -> None:
    user_data = login_attempts.get(username, {"attempts": 0, "blocked_until": None})
    user_data["attempts"] += 1

    if user_data["attempts"] >= MAX_ATTEMPTS:
        user_data["blocked_until"] = datetime.datetime.now() + BLOCK_DURATION

    login_attempts[username] = user_data

def reset_attempts(username: str) -> None:
    login_attempts[username] = {"attempts": 0, "blocked_until": None}
