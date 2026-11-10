from sqlalchemy.orm import Session

from . import models, schemas


# ---------- Doctor ----------
def create_doctor(db: Session, doctor: schemas.DoctorCreate) -> models.Doctor:
    db_doctor = models.Doctor(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def get_doctors(db: Session):
    return db.query(models.Doctor).all()


def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()


# ---------- Availability ----------
def add_availability(
    db: Session, doctor_id: int, slot: schemas.AvailabilityCreate
) -> models.Availability:
    db_slot = models.Availability(doctor_id=doctor_id, **slot.model_dump())
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot


def get_availabilities(db: Session, doctor_id: int):
    return (
        db.query(models.Availability)
        .filter(models.Availability.doctor_id == doctor_id)
        .all()
    )


def get_availability(db: Session, slot_id: int):
    return (
        db.query(models.Availability)
        .filter(models.Availability.id == slot_id)
        .first()
    )


def set_slot_booked(db: Session, slot_id: int, booked: bool):
    slot = get_availability(db, slot_id)
    if slot is None:
        return None
    slot.is_booked = booked
    db.commit()
    db.refresh(slot)
    return slot

