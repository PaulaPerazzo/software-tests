import re
from fastapi import HTTPException

def validate_password(password: str) -> bool:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="the password should have at least 8 caracters.")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="the password should have at least 1 uppercase caracter.")
    if not re.search(r'[0-9]', password):
        raise HTTPException(status_code=400, detail="the password should have at least 1 number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise HTTPException(status_code=400, detail="the password should have at least 1 special caracter.")
    
    return True
