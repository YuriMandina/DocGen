# backend/schemas.py
from datetime import date
from typing import Optional

from models import ContractType

from pydantic import BaseModel, Field, EmailStr, model_validator


# =====================================================================
#                        DOMÍNIO: EMPRESA E USUÁRIO
# =====================================================================


class CompanyBase(BaseModel):
    business_name: str = Field(..., description="Razão Social ou Nome Fantasia")
    cnpj: str = Field(
        ...,
        pattern=r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$",
        description="Formato: 00.000.000/0000-00",
    )


class CompanyResponse(CompanyBase):
    id: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Dados necessários para o registro inicial."""

    username: EmailStr = Field(..., description="E-mail corporativo será o login")
    password: str = Field(..., min_length=8, description="Senha forte")
    password_confirm: str = Field(..., description="Confirmação da senha")
    full_name: str = Field(..., description="Nome completo do usuário")
    cpf: str = Field(
        ...,
        pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$",
        description="Formato: 000.000.000-00",
    )

    # Dados da empresa que o usuário diz pertencer
    company_name: str
    cnpj: str = Field(..., pattern=r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserCreate":
        # getattr evita o erro caso o Pydantic falhe em injetar o campo antes da validação final
        if getattr(self, "password", None) != getattr(self, "password_confirm", None):
            raise ValueError("As senhas não coincidem.")
        return self


class UserResponse(BaseModel):
    """O que devolvemos para o Frontend (NUNCA devolver a senha)"""

    id: int
    username: str
    full_name: str
    cpf: str
    is_master: bool
    is_approved: bool
    company_id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


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
