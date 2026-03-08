# backend/crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
import models
import schemas

# =====================================================================
#                        GESTÃO DE CARGOS (ROLES)
# =====================================================================


def get_role_by_id(db: Session, role_id: int) -> Optional[models.Role]:
    """Busca um cargo específico pelo seu ID."""
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[models.Role]:
    """Busca um cargo específico pelo nome exato."""
    return db.query(models.Role).filter(models.Role.name == name).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Role]:
    """Retorna uma lista paginada de todos os cargos."""
    return db.query(models.Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: schemas.RoleCreate) -> models.Role:
    """Cria e salva um novo cargo no banco de dados."""
    db_role = models.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(
    db: Session, role_id: int, role: schemas.RoleCreate
) -> Optional[models.Role]:
    """Atualiza o nome de um cargo existente."""
    db_role = get_role_by_id(db, role_id)
    if db_role:
        db_role.name = role.name
        db.commit()
        db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int) -> Optional[models.Role]:
    """Remove um cargo do banco de dados pelo ID."""
    db_role = get_role_by_id(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()
    return db_role


# =====================================================================
#                   GESTÃO DE FUNCIONÁRIOS (EMPLOYEES)
# =====================================================================


def get_employee_by_id(db: Session, employee_id: int) -> Optional[models.Employee]:
    """Busca um funcionário específico pelo seu ID."""
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def get_employees(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Employee]:
    """Retorna uma lista paginada de todos os funcionários."""
    return db.query(models.Employee).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: schemas.EmployeeCreate) -> models.Employee:
    """Cria e salva um novo funcionário."""
    # Desempacota os dados do Pydantic (validados) direto para o SQLAlchemy
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(
    db: Session, employee_id: int, employee: schemas.EmployeeCreate
) -> Optional[models.Employee]:
    """Atualiza os dados de um funcionário existente dinamicamente."""
    db_employee = get_employee_by_id(db, employee_id)

    if db_employee:
        # Pega os dados validados que chegaram da API
        update_data = employee.model_dump(exclude_unset=True)

        # Atualiza apenas os campos enviados, de forma dinâmica e limpa
        for key, value in update_data.items():
            setattr(db_employee, key, value)

        db.commit()
        db.refresh(db_employee)

    return db_employee


def delete_employee(db: Session, employee_id: int) -> Optional[models.Employee]:
    """Remove um funcionário do banco de dados pelo ID."""
    db_employee = get_employee_by_id(db, employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
    return db_employee
