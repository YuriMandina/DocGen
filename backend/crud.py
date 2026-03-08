# backend/crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
import models
import schemas

# =====================================================================
#                        GESTÃO DE CARGOS (ROLES)
# =====================================================================


def get_role_by_id(db: Session, role_id: int, company_id: int) -> Optional[models.Role]:
    """Busca um cargo específico garantindo que pertence à empresa atual."""
    return (
        db.query(models.Role)
        .filter(models.Role.id == role_id, models.Role.company_id == company_id)
        .first()
    )


def get_role_by_name(db: Session, name: str, company_id: int) -> Optional[models.Role]:
    """Busca um cargo pelo nome dentro da empresa específica."""
    return (
        db.query(models.Role)
        .filter(models.Role.name == name, models.Role.company_id == company_id)
        .first()
    )


def get_roles(
    db: Session, company_id: int, skip: int = 0, limit: int = 100
) -> List[models.Role]:
    """Retorna cargos APENAS da empresa do usuário logado."""
    return (
        db.query(models.Role)
        .filter(models.Role.company_id == company_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_role(db: Session, role: schemas.RoleCreate, company_id: int) -> models.Role:
    """Cria um cargo vinculando-o à empresa atual."""
    db_role = models.Role(name=role.name, company_id=company_id)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(
    db: Session, role_id: int, role: schemas.RoleCreate, company_id: int
) -> Optional[models.Role]:
    db_role = get_role_by_id(db, role_id, company_id)
    if db_role:
        db_role.name = role.name
        db.commit()
        db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int, company_id: int) -> Optional[models.Role]:
    db_role = get_role_by_id(db, role_id, company_id)
    if db_role:
        db.delete(db_role)
        db.commit()
    return db_role


# =====================================================================
#                   GESTÃO DE FUNCIONÁRIOS (EMPLOYEES)
# =====================================================================


def get_employee_by_id(
    db: Session, employee_id: int, company_id: int
) -> Optional[models.Employee]:
    return (
        db.query(models.Employee)
        .filter(
            models.Employee.id == employee_id, models.Employee.company_id == company_id
        )
        .first()
    )


def get_employees(
    db: Session, company_id: int, skip: int = 0, limit: int = 100
) -> List[models.Employee]:
    return (
        db.query(models.Employee)
        .filter(models.Employee.company_id == company_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_employee(
    db: Session, employee: schemas.EmployeeCreate, company_id: int
) -> models.Employee:
    # Desempacota os dados e injeta o company_id silenciosamente
    employee_data = employee.model_dump()
    db_employee = models.Employee(**employee_data, company_id=company_id)

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(
    db: Session, employee_id: int, employee: schemas.EmployeeCreate, company_id: int
) -> Optional[models.Employee]:
    db_employee = get_employee_by_id(db, employee_id, company_id)
    if db_employee:
        update_data = employee.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee


def delete_employee(
    db: Session, employee_id: int, company_id: int
) -> Optional[models.Employee]:
    db_employee = get_employee_by_id(db, employee_id, company_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
    return db_employee
