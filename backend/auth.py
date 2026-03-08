# backend/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
import security
from database import get_db
from dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# =====================================================================
#
# =====================================================================


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário com Integridade Transacional (All-or-Nothing).
    """
    # 1. Verifica duplicidade
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    if db.query(models.User).filter(models.User.cpf == user_in.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado.")

    # 2. Gera o Hash da senha PRIMEIRO. Se der erro aqui, nem tocamos no banco de dados.
    hashed_password = security.get_password_hash(user_in.password)

    # 3. Verifica a Empresa pelo CNPJ
    company = (
        db.query(models.Company).filter(models.Company.cnpj == user_in.cnpj).first()
    )

    is_master = False
    is_approved = False

    if not company:
        # Primeira vez deste CNPJ: Cria a empresa
        company = models.Company(business_name=user_in.company_name, cnpj=user_in.cnpj)
        db.add(company)
        db.flush()  # <-- MÁGICA: Prepara a inserção e pega o ID, mas NÃO salva ainda!
        is_master = True
        is_approved = True
    else:
        # Empresa já existe: Valida o nome
        if company.business_name.lower() != user_in.company_name.lower():
            raise HTTPException(
                status_code=400,
                detail="CNPJ já registrado com uma Razão Social diferente.",
            )

    # 4. Cria o usuário
    new_user = models.User(
        username=user_in.username,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        cpf=user_in.cpf,
        is_master=is_master,
        is_approved=is_approved,
        company_id=company.id,
    )

    db.add(new_user)

    # 5. Salva TUDO JUNTO de uma vez (Empresa e Usuário). Se falhar, faz rollback de tudo.
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Autentica o usuário e devolve o JWT Token."""
    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )

    # Previne "Timing Attacks" e não dá dicas se o email ou a senha estão errados
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sua conta está aguardando aprovação do administrador da empresa.",
        )

    # Gera o Token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def get_user_me(current_user: models.User = Depends(get_current_active_user)):
    """Devolve os dados do próprio usuário autenticado."""
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_user_me(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """Atualiza os dados cadastrais do usuário logado."""
    # Verifica se o novo email ou cpf já pertencem a OUTRO usuário
    if (
        db.query(models.User)
        .filter(
            models.User.username == user_in.username, models.User.id != current_user.id
        )
        .first()
    ):
        raise HTTPException(
            status_code=400, detail="Este E-mail já está em uso por outra conta."
        )
    if (
        db.query(models.User)
        .filter(models.User.cpf == user_in.cpf, models.User.id != current_user.id)
        .first()
    ):
        raise HTTPException(
            status_code=400, detail="Este CPF já está em uso por outra conta."
        )

    current_user.full_name = user_in.full_name
    current_user.username = user_in.username
    current_user.cpf = user_in.cpf

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/password")
def update_password(
    pass_in: schemas.PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """Troca a senha do usuário logado com validação da senha atual."""
    if not security.verify_password(
        pass_in.current_password, current_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="A senha atual está incorreta.")

    current_user.hashed_password = security.get_password_hash(pass_in.new_password)
    db.commit()
    return {"message": "Senha atualizada com sucesso."}
