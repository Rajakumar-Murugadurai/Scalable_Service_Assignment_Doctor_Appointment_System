from datetime import date, time

from pydantic import BaseModel, EmailStr


# ---------- Doctor ----------
class DoctorBase(BaseModel):
    name: str
    specialization: str
    email: EmailStr


class DoctorCreate(DoctorBase):
    pass


class Doctor(DoctorBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Availability ----------
class AvailabilityBase(BaseModel):
    day: date
    start_time: time
    end_time: time


class AvailabilityCreate(AvailabilityBase):
    pass


class Availability(AvailabilityBase):
    id: int
    doctor_id: int
    is_booked: bool

    class Config:
        from_attributes = True

