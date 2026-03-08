# backend/models.py
import enum

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, LargeBinary
from sqlalchemy.orm import relationship

from database import Base

# =====================================================================
#                        ENUMERAÇÕES GERAIS
# =====================================================================


class ContractType(enum.Enum):
    """Define as regras de acesso e visibilidade de um contrato."""

    UNIVERSAL = "UNIVERSAL"
    ESPECIFICO = "ESPECIFICO"


# =====================================================================
#                        TABELA: CARGOS (ROLES)
# =====================================================================


class Role(Base):
    """Entidade que representa os cargos organizacionais cadastrados no sistema."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # Relacionamentos (Bidirecionais) para facilitar buscas cruzadas
    employees = relationship("Employee", back_populates="role")
    contracts = relationship("ContractTemplate", back_populates="role")


# =====================================================================
#                 TABELA: FUNCIONÁRIOS (EMPLOYEES)
# =====================================================================


class Employee(Base):
    """Entidade central de armazenamento dos dados dos colaboradores."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    admission_date = Column(Date, nullable=False)

    # Restrição de unicidade: Duas pessoas não podem ter a mesma carteira
    professional_card = Column(String, unique=True, nullable=False)

    # Relacionamento com a tabela de Cargos
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", back_populates="employees")


# =====================================================================
#             TABELA: MODELOS DE CONTRATO (TEMPLATES)
# =====================================================================


class ContractTemplate(Base):
    """Armazena os metadados e o ARQUIVO FÍSICO em formato binário."""

    __tablename__ = "contract_templates"

    id = Column(Integer, primary_key=True, index=True)
    contract_name = Column(String, nullable=False)

    file_data = Column(LargeBinary, nullable=False)

    type = Column(Enum(ContractType), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    role = relationship("Role", back_populates="contracts")
