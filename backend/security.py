# backend/security.py
import os

from datetime import datetime, timedelta
from typing import Optional

import bcrypt

from jose import JWTError, jwt

from dotenv import load_dotenv

load_dotenv()

# Configurações do JWT
SECRET_KEY = os.getenv("SECRET_KEY", "chave_fallback_insegura_mude_isso")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

if not os.getenv("SECRET_KEY"):
    print("AVISO: SECRET_KEY não encontrada no .env. Usando fallback inseguro.")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash."""
    # bcrypt exige bytes, então precisamos encodar as strings
    password_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")

    try:
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    """Gera o hash Bcrypt da senha para salvar no banco."""
    # 1. Encodar a senha para bytes
    password_bytes = password.encode("utf-8")

    # 2. Gerar o salt
    salt = bcrypt.gensalt()

    # 3. Gerar o hash (ele já inclui o salt na string final)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # 4. Retornar como string para o SQLAlchemy salvar no banco
    return hashed_bytes.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Gera um token JWT contendo os dados do usuário."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
