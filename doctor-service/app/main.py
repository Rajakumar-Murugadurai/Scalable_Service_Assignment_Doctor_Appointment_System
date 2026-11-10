from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import get_db, init_db

# Create tables on startup, retrying until Postgres is reachable
# (Postgres container may boot slower than the app).
init_db()

app = FastAPI(
    title="Doctor Service",
    description="Manages doctors and their availability slots (Telehealth app).",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    # Ensure tables exist once the app is fully up (self-healing safety net).
    init_db()



@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "doctor-service"}


# ---------- Doctor endpoints ----------
@app.post("/doctors", response_model=schemas.Doctor, tags=["doctors"])
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    return crud.create_doctor(db, doctor)


@app.get("/doctors", response_model=list[schemas.Doctor], tags=["doctors"])
def list_doctors(db: Session = Depends(get_db)):
    return crud.get_doctors(db)


@app.get("/doctors/{doctor_id}", response_model=schemas.Doctor, tags=["doctors"])
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = crud.get_doctor(db, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


# ---------- Availability endpoints ----------
@app.post(
    "/doctors/{doctor_id}/availability",
    response_model=schemas.Availability,
    tags=["availability"],
)
def add_availability(
    doctor_id: int,
    slot: schemas.AvailabilityCreate,
    db: Session = Depends(get_db),
):
    if crud.get_doctor(db, doctor_id) is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return crud.add_availability(db, doctor_id, slot)


@app.get(
    "/doctors/{doctor_id}/availability",
    response_model=list[schemas.Availability],
    tags=["availability"],
)
def list_availability(doctor_id: int, db: Session = Depends(get_db)):
    return crud.get_availabilities(db, doctor_id)


@app.get(
    "/availability/{slot_id}",
    response_model=schemas.Availability,
    tags=["availability"],
)
def get_slot(slot_id: int, db: Session = Depends(get_db)):
    slot = crud.get_availability(db, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot


@app.patch(
    "/availability/{slot_id}/book",
    response_model=schemas.Availability,
    tags=["availability"],
)
def book_slot(slot_id: int, db: Session = Depends(get_db)):
    """Called by Appointment Service to reserve a slot."""
    slot = crud.get_availability(db, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    if slot.is_booked:
        raise HTTPException(status_code=409, detail="Slot already booked")
    return crud.set_slot_booked(db, slot_id, True)


@app.patch(
    "/availability/{slot_id}/release",
    response_model=schemas.Availability,
    tags=["availability"],
)
def release_slot(slot_id: int, db: Session = Depends(get_db)):
    """Called by Appointment Service when an appointment is cancelled."""
    slot = crud.get_availability(db, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    return crud.set_slot_booked(db, slot_id, False)


