from fastapi import APIRouter, HTTPException
from auth.models import UserCreate, UserLogin
from auth.validations import validate_password
from auth.utils import record_failed_attempt, check_user_block, reset_attempts
import pandas as pd

router = APIRouter()

# database simulation
users_df = pd.DataFrame(columns=["username", "password"])

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    global users_df  
    validate_password(user.password)
    
    if user.username in users_df["username"].values:
        raise HTTPException(status_code=400, detail="user already exists.")
    
    new_entry = pd.DataFrame([{"username": user.username, "password": user.password}])
    users_df = pd.concat([users_df, new_entry], ignore_index=True)
    
    return {
        "message": "user registered.",
        "user": {"username": user.username}
    }

@router.post("/login", response_model=dict)
async def login(user: UserLogin):
    global users_df
    if user.username not in users_df["username"].values:
        raise HTTPException(status_code=404, detail="unknown user.")
    
    if check_user_block(user.username):
        raise HTTPException(status_code=403, detail="user blocked. try again later.")
    
    user_data = users_df.loc[users_df["username"] == user.username].iloc[0]
    
    if user.password != user_data["password"]:
        record_failed_attempt(user.username)
        raise HTTPException(status_code=401, detail="wrong password.")
    
    reset_attempts(user.username)
    
    return {
        "message": "sucssesful login.",
        "user": {"username": user.username}
    }
