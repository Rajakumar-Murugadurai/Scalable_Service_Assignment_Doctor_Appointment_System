from datetime import datetime

from pydantic import BaseModel, EmailStr


class AppointmentCreate(BaseModel):
    patient_name: str
    patient_email: EmailStr
    doctor_id: int
    slot_id: int


class Appointment(BaseModel):
    id: int
    patient_name: str
    patient_email: EmailStr
    doctor_id: int
    slot_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

