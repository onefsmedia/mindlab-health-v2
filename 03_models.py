"""
MindLab Health - SQLAlchemy Models
==================================
Database models for users, appointments, and messages
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class UserRole(enum.Enum):
    """User role enumeration"""
    patient = "patient"
    therapist = "therapist"
    admin = "admin"

class AppointmentStatus(enum.Enum):
    """Appointment status enumeration"""
    scheduled = "scheduled"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="patient")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments_as_patient = relationship(
        "Appointment",
        foreign_keys="Appointment.user_id",
        back_populates="patient"
    )
    appointments_as_therapist = relationship(
        "Appointment",
        foreign_keys="Appointment.therapist_id",
        back_populates="therapist"
    )
    sent_messages = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender"
    )
    received_messages = relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        back_populates="recipient"
    )

class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_datetime = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="scheduled")
    notes = Column(Text)
    
    # Relationships
    patient = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="appointments_as_patient"
    )
    therapist = relationship(
        "User",
        foreign_keys=[therapist_id],
        back_populates="appointments_as_therapist"
    )

class Message(Base):
    """Message model"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )
    recipient = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="received_messages"
    )
