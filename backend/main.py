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

# =====================================================================
#                        CONFIGURAÇÃO E SETUP
# =====================================================================

# Cria as tabelas no PostgreSQL automaticamente caso elas não existam
models.Base.metadata.create_all(bind=engine)

# Garante a existência das pastas físicas para armazenamento de documentos
os.makedirs("templates", exist_ok=True)
os.makedirs("templates/generated", exist_ok=True)

app = FastAPI(
    title="Sistema de Contratos API",
    description="API para gestão de RH e geração automatizada de contratos de trabalho.",
    version="1.1.0",
)

# Configuração de CORS para permitir comunicação com o Vue.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar o domínio correto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
#                        ROTAS: CARGOS (ROLES)
# =====================================================================


@app.post("/roles/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Cadastra um novo cargo no sistema."""
    db_role = crud.get_role_by_name(db, name=role.name)
    if db_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cargo já cadastrado no sistema.",
        )
    return crud.create_role(db=db, role=role)


@app.get("/roles/", response_model=List[schemas.Role])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os cargos cadastrados."""
    return crud.get_roles(db, skip=skip, limit=limit)


@app.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(role_id: int, role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Atualiza as informações de um cargo existente."""
    db_role = crud.update_role(db, role_id, role)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado."
        )
    return db_role


@app.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Remove um cargo (bloqueado se houver funcionários vinculados)."""
    try:
        db_role = crud.delete_role(db, role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado."
            )
        return {"message": "Cargo excluído com sucesso."}
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Não é possível excluir este cargo pois existem "
                "funcionários vinculados a ele."
            ),
        ) from exc


# =====================================================================
#                   ROTAS: FUNCIONÁRIOS (EMPLOYEES)
# =====================================================================


@app.post(
    "/employees/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED
)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    """Cadastra um novo funcionário, validando cargo e unicidade da carteira."""
    db_role = crud.get_role_by_id(db, employee.role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado."
        )

    db_emp = (
        db.query(models.Employee)
        .filter(models.Employee.professional_card == employee.professional_card)
        .first()
    )
    if db_emp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Carteira Profissional já cadastrada no sistema.",
        )

    return crud.create_employee(db=db, employee=employee)


@app.get("/employees/", response_model=List[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os funcionários cadastrados."""
    return crud.get_employees(db, skip=skip, limit=limit)


@app.put("/employees/{employee_id}", response_model=schemas.Employee)
def update_employee(
    employee_id: int, employee: schemas.EmployeeCreate, db: Session = Depends(get_db)
):
    """Atualiza os dados de um funcionário."""
    db_role = crud.get_role_by_id(db, employee.role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado."
        )

    # Valida se a carteira já está em uso por OUTRO funcionário
    db_emp_check = (
        db.query(models.Employee)
        .filter(
            models.Employee.professional_card == employee.professional_card,
            models.Employee.id != employee_id,
        )
        .first()
    )
    if db_emp_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Carteira Profissional já cadastrada para outro funcionário.",
        )

    db_employee = crud.update_employee(db, employee_id, employee)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado."
        )
    return db_employee


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Remove um funcionário do sistema."""
    db_employee = crud.delete_employee(db, employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado."
        )
    return {"message": "Funcionário excluído com sucesso."}


# =====================================================================
#               ROTAS: MODELOS DE CONTRATO (TEMPLATES)
# =====================================================================


@app.get("/contracts/", response_model=List[schemas.ContractTemplate])
def read_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.ContractTemplate).offset(skip).limit(limit).all()


# NOTA: Usamos `async def` aqui para podermos usar o `await file.read()`
@app.post("/contracts/upload/", status_code=status.HTTP_201_CREATED)
async def upload_contract_template(
    contract_name: str = Form(...),
    contract_type: models.ContractType = Form(..., alias="type"),
    role_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos .docx são permitidos.",
        )

    if contract_type == models.ContractType.ESPECIFICO and not role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contratos específicos exigem a vinculação a um cargo.",
        )

    # 1. Lê o arquivo INTEIRO para a memória RAM (Bytes)
    file_content = await file.read()

    # 2. Converte para um Stream compatível com a biblioteca python-docx
    file_stream = io.BytesIO(file_content)

    # 3. Valida as tags direto da RAM
    missing_tags = document_processor.check_tags_in_docx(file_stream)
    if missing_tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload recusado. Faltam as seguintes tags obrigatórias no documento: {', '.join(missing_tags)}",
        )

    # 4. Salva a sequencia de Bytes diretamente no PostgreSQL
    db_contract = models.ContractTemplate(
        contract_name=contract_name,
        file_data=file_content,  # Salvando de forma segura no banco
        type=contract_type,
        role_id=role_id,
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return {
        "message": "Contrato salvo com segurança no banco de dados!",
        "contract_id": db_contract.id,
    }


@app.delete("/contracts/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = (
        db.query(models.ContractTemplate)
        .filter(models.ContractTemplate.id == contract_id)
        .first()
    )
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo de contrato não encontrado.",
        )

    # Como o arquivo vive no banco, deletar a linha destrói o arquivo para sempre.
    db.delete(contract)
    db.commit()
    return {"message": "Modelo de contrato excluído com sucesso."}


# =====================================================================
#                  ROTAS: GERAÇÃO DE CONTRATOS (MOTOR)
# =====================================================================


@app.post("/contracts/generate/")
def generate_employee_contract(
    request: schemas.ContractGenerateRequest, db: Session = Depends(get_db)
):
    employee = crud.get_employee_by_id(db, request.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado."
        )

    contract = (
        db.query(models.ContractTemplate)
        .filter(models.ContractTemplate.id == request.contract_id)
        .first()
    )
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo de contrato não encontrado.",
        )

    if (
        contract.type == models.ContractType.ESPECIFICO
        and contract.role_id != employee.role_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este contrato é específico para outro cargo e não se aplica a este funcionário.",
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

    try:
        # 1. Pega os dados binários do banco e transforma em fluxo de leitura
        template_stream = io.BytesIO(contract.file_data)

        # 2. Processa o arquivo 100% na memória RAM
        final_file_stream = document_processor.fill_contract(
            file_stream=template_stream, context=context
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar o documento: {str(e)}",
        ) from e

    safe_name = employee.full_name.replace(" ", "_")
    output_filename = f"{contract.contract_name}_{safe_name}.docx"

    # 3. Devolve a memória direto para o navegador e limpa os rastros
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
    request: ContractBatchGenerateRequest, db: Session = Depends(get_db)
):
    employee = crud.get_employee_by_id(db, request.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado."
        )

    # Prepara dados de contexto que são os mesmos para todos os contratos
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
                .filter(models.ContractTemplate.id == contract_id)
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
                    file_stream=template_stream, context=context
                )
                safe_contract_name = contract.contract_name.replace(" ", "_").replace(
                    "/", "-"
                )
                docx_filename = f"{safe_contract_name}_{safe_employee_name}.docx"
                zip_file.writestr(docx_filename, final_file_stream.getvalue())
                generated_count += 1
            except (ValueError, AttributeError, OSError) as e:
                print(
                    f"Erro ao gerar contrato {contract.id} para funcionário {employee.id}: {e}"
                )
                continue

    if generated_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum contrato compatível foi encontrado ou um erro ocorreu durante a geração.",
        )

    zip_buffer.seek(0)
    zip_filename = f"Contratos_{safe_employee_name}.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
    )
