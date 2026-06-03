from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.center import YouthCenterCreate, YouthCenterUpdate


def get_youth_center(db: Session, center_id: int) -> Optional[models.YouthCenter]:
    return db.query(models.YouthCenter).filter(models.YouthCenter.id == center_id).first()


def get_youth_centers(db: Session, skip: int = 0, limit: int = 100) -> List[models.YouthCenter]:
    return db.query(models.YouthCenter).offset(skip).limit(limit).all()


def create_youth_center(db: Session, center_in: YouthCenterCreate) -> models.YouthCenter:
    center = models.YouthCenter(**center_in.dict())
    db.add(center)
    db.commit()
    db.refresh(center)
    return center


def update_youth_center(db: Session, center_id: int, center_in: YouthCenterUpdate) -> Optional[models.YouthCenter]:
    center = get_youth_center(db, center_id)
    if center is None:
        return None

    update_data = center_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(center, field, value)

    db.add(center)
    db.commit()
    db.refresh(center)
    return center


def deactivate_youth_center(db: Session, center_id: int) -> Optional[models.YouthCenter]:
    center = get_youth_center(db, center_id)
    if center is None:
        return None

    center.is_active = False
    db.add(center)
    db.commit()
    db.refresh(center)
    return center
