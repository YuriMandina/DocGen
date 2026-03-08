# backend/main.py
import os
import io
import zipfile
from datetime import date
from typing import List, Optional

from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
import crud
import document_processor
from database import engine, get_db

# NOVO: Importações de Autenticação e Segurança
from auth import router as auth_router
from dependencies import get_current_active_user, get_current_master_user

models.Base.metadata.create_all(bind=engine)
os.makedirs("templates", exist_ok=True)
os.makedirs("templates/generated", exist_ok=True)

app = FastAPI(
    title="Sistema de Contratos API (SaaS Multi-tenant)",
    description="API com isolamento de dados por empresa e aprovação de usuários.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Acopla as rotas de login e registro
app.include_router(auth_router)

# =====================================================================
#                ROTAS: APROVAÇÃO DE USUÁRIOS (MASTER ONLY)
# =====================================================================


@app.get("/users/pending", response_model=List[schemas.UserResponse])
def get_pending_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_master_user),  # Exige ser MASTER
):
    """Lista usuários da mesma empresa que estão aguardando aprovação."""
    return (
        db.query(models.User)
        .filter(
            models.User.company_id == current_user.company_id,
            models.User.is_approved == False,
        )
        .all()
    )


@app.put("/users/{user_id}/approve", response_model=schemas.UserResponse)
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_master_user),
):
    """Aprova a entrada de um novo usuário na empresa."""
    user = (
        db.query(models.User)
        .filter(
            models.User.id == user_id, models.User.company_id == current_user.company_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404, detail="Usuário não encontrado nesta empresa."
        )

    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user


# =====================================================================
#                        ROTAS: CARGOS (ROLES)
# =====================================================================


@app.post("/roles/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
def create_role(
    role: schemas.RoleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    db_role = crud.get_role_by_name(
        db, name=role.name, company_id=current_user.company_id
    )
    if db_role:
        raise HTTPException(
            status_code=400, detail="Cargo já cadastrado na sua empresa."
        )
    return crud.create_role(db=db, role=role, company_id=current_user.company_id)


@app.get("/roles/", response_model=List[schemas.Role])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    return crud.get_roles(
        db, company_id=current_user.company_id, skip=skip, limit=limit
    )


@app.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(
    role_id: int,
    role: schemas.RoleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    db_role = crud.update_role(db, role_id, role, current_user.company_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Cargo não encontrado.")
    return db_role


@app.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    try:
        db_role = crud.delete_role(db, role_id, current_user.company_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Cargo não encontrado.")
        return {"message": "Cargo excluído."}
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Existem funcionários vinculados a este cargo."
        ) from exc


# =====================================================================
#                   ROTAS: FUNCIONÁRIOS (EMPLOYEES)
# =====================================================================


@app.post(
    "/employees/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED
)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    db_role = crud.get_role_by_id(db, employee.role_id, current_user.company_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Cargo não encontrado.")

    # Verifica duplicidade APENAS dentro da mesma empresa
    db_emp = (
        db.query(models.Employee)
        .filter(
            models.Employee.professional_card == employee.professional_card,
            models.Employee.company_id == current_user.company_id,
        )
        .first()
    )
    if db_emp:
        raise HTTPException(
            status_code=400, detail="Carteira já cadastrada na sua empresa."
        )

    return crud.create_employee(
        db=db, employee=employee, company_id=current_user.company_id
    )


@app.get("/employees/", response_model=List[schemas.Employee])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    return crud.get_employees(
        db, company_id=current_user.company_id, skip=skip, limit=limit
    )


@app.put("/employees/{employee_id}", response_model=schemas.Employee)
def update_employee(
    employee_id: int,
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    db_role = crud.get_role_by_id(db, employee.role_id, current_user.company_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Cargo não encontrado.")

    db_employee = crud.update_employee(
        db, employee_id, employee, current_user.company_id
    )
    if not db_employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
    return db_employee


@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    db_employee = crud.delete_employee(db, employee_id, current_user.company_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
    return {"message": "Funcionário excluído."}


# =====================================================================
#               ROTAS: MODELOS DE CONTRATO (TEMPLATES)
# =====================================================================


@app.get("/contracts/", response_model=List[schemas.ContractTemplate])
def read_contracts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    # Lista apenas os contratos da empresa atual
    return (
        db.query(models.ContractTemplate)
        .filter(models.ContractTemplate.company_id == current_user.company_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.post("/contracts/upload/", status_code=status.HTTP_201_CREATED)
async def upload_contract_template(
    contract_name: str = Form(...),
    contract_type: models.ContractType = Form(..., alias="type"),
    role_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .docx.")
    if contract_type == models.ContractType.ESPECIFICO and not role_id:
        raise HTTPException(
            status_code=400, detail="Contratos específicos exigem cargo."
        )

    file_content = await file.read()
    file_stream = io.BytesIO(file_content)
    missing_tags = document_processor.check_tags_in_docx(file_stream)

    if missing_tags:
        raise HTTPException(
            status_code=400, detail=f"Faltam tags: {', '.join(missing_tags)}"
        )

    db_contract = models.ContractTemplate(
        contract_name=contract_name,
        file_data=file_content,
        type=contract_type,
        role_id=role_id,
        company_id=current_user.company_id,  # Vínculo com a empresa
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return {"message": "Salvo com sucesso!", "contract_id": db_contract.id}


@app.delete("/contracts/{contract_id}")
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    contract = (
        db.query(models.ContractTemplate)
        .filter(
            models.ContractTemplate.id == contract_id,
            models.ContractTemplate.company_id == current_user.company_id,
        )
        .first()
    )

    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")

    db.delete(contract)
    db.commit()
    return {"message": "Modelo excluído."}


# =====================================================================
#                  ROTAS: GERAÇÃO DE CONTRATOS
# =====================================================================


@app.post("/contracts/generate/")
def generate_employee_contract(
    request: schemas.ContractGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    employee = crud.get_employee_by_id(db, request.employee_id, current_user.company_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    contract = (
        db.query(models.ContractTemplate)
        .filter(
            models.ContractTemplate.id == request.contract_id,
            models.ContractTemplate.company_id == current_user.company_id,
        )
        .first()
    )

    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")

    if (
        contract.type == models.ContractType.ESPECIFICO
        and contract.role_id != employee.role_id
    ):
        raise HTTPException(
            status_code=400, detail="Contrato incompatível com o cargo."
        )

    target_date = (
        request.custom_date if request.custom_date else employee.admission_date
    )
    meses_pt = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]
    formatted_date = (
        f"{target_date.day} de {meses_pt[target_date.month - 1]} de {target_date.year}"
    )

    context = {
        "[NOME DO COLABORADOR]": employee.full_name,
        "[NÚMERO DA CARTEIRA]": employee.professional_card,
        "[DIA, MÊS E ANO]": formatted_date,
    }

    template_stream = io.BytesIO(contract.file_data)
    final_file_stream = document_processor.fill_contract(template_stream, context)

    safe_name = employee.full_name.replace(" ", "_")
    output_filename = f"{contract.contract_name}_{safe_name}.docx"

    return StreamingResponse(
        final_file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{output_filename}"'},
    )


class ContractBatchGenerateRequest(BaseModel):
    employee_id: int
    contract_ids: List[int]
    custom_date: Optional[date] = None


@app.post("/contracts/generate-batch/")
def generate_contracts_batch(
    request: ContractBatchGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    employee = crud.get_employee_by_id(db, request.employee_id, current_user.company_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    target_date = (
        request.custom_date if request.custom_date else employee.admission_date
    )
    meses_pt = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]
    formatted_date = (
        f"{target_date.day} de {meses_pt[target_date.month - 1]} de {target_date.year}"
    )

    context = {
        "[NOME DO COLABORADOR]": employee.full_name,
        "[NÚMERO DA CARTEIRA]": employee.professional_card,
        "[DIA, MÊS E ANO]": formatted_date,
    }

    safe_employee_name = employee.full_name.replace(" ", "_")
    zip_buffer = io.BytesIO()
    generated_count = 0

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for contract_id in request.contract_ids:
            contract = (
                db.query(models.ContractTemplate)
                .filter(
                    models.ContractTemplate.id == contract_id,
                    models.ContractTemplate.company_id == current_user.company_id,
                )
                .first()
            )

            if not contract or (
                contract.type == models.ContractType.ESPECIFICO
                and contract.role_id != employee.role_id
            ):
                continue

            try:
                template_stream = io.BytesIO(contract.file_data)
                final_file_stream = document_processor.fill_contract(
                    template_stream, context
                )
                safe_contract_name = contract.contract_name.replace(" ", "_").replace(
                    "/", "-"
                )
                docx_filename = f"{safe_contract_name}_{safe_employee_name}.docx"
                zip_file.writestr(docx_filename, final_file_stream.getvalue())
                generated_count += 1
            except Exception:
                continue

    if generated_count == 0:
        raise HTTPException(status_code=400, detail="Nenhum contrato gerado.")

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="Contratos_{safe_employee_name}.zip"'
        },
    )
