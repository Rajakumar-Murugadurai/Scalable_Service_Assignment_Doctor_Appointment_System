from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship

from .database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    availabilities = relationship(
        "Availability", back_populates="doctor", cascade="all, delete-orphan"
    )


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    day = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_booked = Column(Boolean, default=False, nullable=False)

    doctor = relationship("Doctor", back_populates="availabilities")

