import os

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db, init_db

# URL of the Doctor Service. In Kubernetes this resolves to the K8s Service DNS
# name (http://doctor-service:8000); locally it defaults to localhost.
DOCTOR_SERVICE_URL = os.getenv("DOCTOR_SERVICE_URL", "http://localhost:8000")

# Create tables on startup, retrying until Postgres is reachable.
init_db()

app = FastAPI(
    title="Appointment Service",
    description="Books patient appointments. Collaborates with the Doctor "
    "Service to validate and reserve availability slots.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    # Ensure tables exist once the app is fully up (self-healing safety net).
    init_db()



@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "appointment-service"}


@app.post("/appointments", response_model=schemas.Appointment, tags=["appointments"])
def create_appointment(
    payload: schemas.AppointmentCreate, db: Session = Depends(get_db)
):
    # 1. Validate the slot exists and belongs to the doctor (call Doctor Service).
    try:
        resp = httpx.get(
            f"{DOCTOR_SERVICE_URL}/availability/{payload.slot_id}", timeout=10.0
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503, detail="Doctor Service unavailable"
        )

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Slot not found")
    slot = resp.json()

    if slot["doctor_id"] != payload.doctor_id:
        raise HTTPException(
            status_code=400, detail="Slot does not belong to this doctor"
        )
    if slot["is_booked"]:
        raise HTTPException(status_code=409, detail="Slot already booked")

    # 2. Reserve the slot in the Doctor Service.
    book_resp = httpx.patch(
        f"{DOCTOR_SERVICE_URL}/availability/{payload.slot_id}/book", timeout=10.0
    )
    if book_resp.status_code != 200:
        raise HTTPException(
            status_code=book_resp.status_code,
            detail="Could not reserve slot: " + book_resp.text,
        )

    # 3. Persist the appointment locally.
    appt = models.Appointment(**payload.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@app.get("/appointments", response_model=list[schemas.Appointment], tags=["appointments"])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()


@app.get(
    "/appointments/{appointment_id}",
    response_model=schemas.Appointment,
    tags=["appointments"],
)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id)
        .first()
    )
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@app.delete("/appointments/{appointment_id}", tags=["appointments"])
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id)
        .first()
    )
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Release the slot back in the Doctor Service.
    try:
        httpx.patch(
            f"{DOCTOR_SERVICE_URL}/availability/{appt.slot_id}/release",
            timeout=10.0,
        )
    except httpx.RequestError:
        pass  # best-effort release

    appt.status = "CANCELLED"
    db.commit()
    return {"message": "Appointment cancelled", "appointment_id": appointment_id}

