from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    patient_email = Column(String, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    slot_id = Column(Integer, nullable=False)
    status = Column(String, default="CONFIRMED", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

