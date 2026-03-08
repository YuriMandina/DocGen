# backend/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import security

# Diz ao FastAPI onde é a URL de login (usada para a documentação interativa /docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Descriptografa o JWT e valida a identidade da requisição."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = (
        db.query(models.User)
        .filter(models.User.username == token_data.username)
        .first()
    )
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    """Garante que o usuário foi aprovado pelo Master antes de deixar acessar a API."""
    if not current_user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seu cadastro ainda está aguardando aprovação do usuário Master da sua empresa.",
        )
    return current_user


def get_current_master_user(
    current_user: models.User = Depends(get_current_active_user),
):
    """Restringe acesso apenas para administradores (usuários master)."""
    if not current_user.is_master:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilégios insuficientes. Apenas usuários Master podem realizar esta ação.",
        )
    return current_user
