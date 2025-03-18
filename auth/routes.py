from fastapi import APIRouter, HTTPException
from auth.models import UserCreate, UserLogin
from auth.validations import validate_password
from auth.utils import record_failed_attempt, check_user_block, reset_attempts
import pandas as pd

router = APIRouter()

# Simulação de um "banco de dados" usando um DataFrame do pandas.
users_df = pd.DataFrame(columns=["username", "password"])

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    global users_df  # Declarando a variável global logo no início da função
    # Valida a senha conforme os critérios de segurança
    validate_password(user.password)
    
    # Verifica se o usuário já está cadastrado
    if user.username in users_df["username"].values:
        raise HTTPException(status_code=400, detail="Usuário já existe.")
    
    # Adiciona o usuário ao DataFrame usando pd.concat
    new_entry = pd.DataFrame([{"username": user.username, "password": user.password}])
    users_df = pd.concat([users_df, new_entry], ignore_index=True)
    
    return {
        "message": "Usuário cadastrado com sucesso.",
        "user": {"username": user.username}
    }

@router.post("/login", response_model=dict)
async def login(user: UserLogin):
    global users_df  # Declarando a variável global no início da função
    # Verifica se o usuário existe
    if user.username not in users_df["username"].values:
        raise HTTPException(status_code=404, detail="Usuário inexistente.")
    
    # Verifica se o usuário está bloqueado
    if check_user_block(user.username):
        raise HTTPException(status_code=403, detail="Usuário bloqueado. Tente novamente mais tarde.")
    
    # Busca os dados do usuário no DataFrame
    user_data = users_df.loc[users_df["username"] == user.username].iloc[0]
    
    # Verifica se a senha está correta
    if user.password != user_data["password"]:
        record_failed_attempt(user.username)
        raise HTTPException(status_code=401, detail="Senha incorreta.")
    
    # Se o login for bem-sucedido, reseta as tentativas de falha
    reset_attempts(user.username)
    
    return {
        "message": "Login realizado com sucesso.",
        "user": {"username": user.username}
    }
