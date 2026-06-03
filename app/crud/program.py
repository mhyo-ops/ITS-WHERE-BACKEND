from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.program import ProgramCreate, ProgramUpdate


def get_program(db: Session, program_id: int) -> Optional[models.Program]:
    return db.query(models.Program).filter(models.Program.id == program_id).first()


def get_programs(db: Session, skip: int = 0, limit: int = 100) -> List[models.Program]:
    return db.query(models.Program).offset(skip).limit(limit).all()


def create_program(db: Session, program_in: ProgramCreate) -> models.Program:
    program = models.Program(**program_in.dict())
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


def update_program(db: Session, program_id: int, program_in: ProgramUpdate) -> Optional[models.Program]:
    program = get_program(db, program_id)
    if program is None:
        return None

    update_data = program_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(program, field, value)

    db.add(program)
    db.commit()
    db.refresh(program)
    return program


def deactivate_program(db: Session, program_id: int) -> Optional[models.Program]:
    program = get_program(db, program_id)
    if program is None:
        return None

    program.is_active = False
    db.add(program)
    db.commit()
    db.refresh(program)
    return program
