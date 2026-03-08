# backend/schemas.py
from datetime import date
from typing import Optional

from models import ContractType

from pydantic import BaseModel, Field


# =====================================================================
#                        DOMÍNIO: CARGOS (ROLES)
# =====================================================================


class RoleCreate(BaseModel):
    """Schema de entrada (Request) para criação e edição de cargos."""

    name: str = Field(
        ..., min_length=2, max_length=100, description="Nome de exibição do cargo"
    )


class Role(RoleCreate):
    """Schema de saída (Response) contendo o identificador único do banco."""

    id: int

    class Config:
        from_attributes = True


# =====================================================================
#                 DOMÍNIO: FUNCIONÁRIOS (EMPLOYEES)
# =====================================================================


class EmployeeCreate(BaseModel):
    """Schema de entrada (Request) para validação rigorosa de colaboradores."""

    full_name: str = Field(
        ..., min_length=3, max_length=255, description="Nome completo do funcionário"
    )
    admission_date: date = Field(
        ..., description="Data formal de ingresso na organização"
    )

    # A Regex barra qualquer lixo que tenha escapado do Frontend (Dupla Segurança)
    professional_card: str = Field(
        ...,
        pattern=r"^\d{8}\/\d{5}-[A-Z]{2}$",
        description="Formato de máscara padronizado: 00123456/00123-UF",
    )
    role_id: int = Field(..., description="Identificador do cargo atrelado")


class Employee(EmployeeCreate):
    """Schema de saída (Response) para a tabela de funcionários."""

    id: int

    class Config:
        from_attributes = True


# =====================================================================
#             DOMÍNIO: MODELOS DE CONTRATO (TEMPLATES)
# =====================================================================


class ContractTemplateBase(BaseModel):
    """Schema para validação dos metadados de arquivos em nuvem/disco."""

    contract_name: str = Field(..., description="Título de identificação do modelo")
    type: ContractType = Field(
        ..., description="Regra de acessibilidade (Universal ou Específico)"
    )
    role_id: Optional[int] = Field(
        None, description="Vinculação de cargo (Nulo se Universal)"
    )


class ContractTemplate(ContractTemplateBase):
    """Schema de saída (Response) listando os contratos disponíveis."""

    id: int

    class Config:
        from_attributes = True


# =====================================================================
#               DOMÍNIO: GERAÇÃO DE DOCUMENTOS (MOTOR)
# =====================================================================


class ContractGenerateRequest(BaseModel):
    """Schema que orquestra a comunicação entre a interface e o processador Word."""

    employee_id: int = Field(
        ..., description="ID do funcionário cujas chaves serão substituídas"
    )
    contract_id: int = Field(
        ..., description="ID do documento base a ser clonado e preenchido"
    )

    # Campo opcional. Se for nulo, a API assume a Data de Admissão automaticamente
    custom_date: Optional[date] = Field(
        None, description="Substituição opcional da tag [DIA, MÊS E ANO]"
    )
