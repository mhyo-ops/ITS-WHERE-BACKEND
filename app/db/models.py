from __future__ import annotations

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, Index, 
    String, Text, Table, func
)
from sqlalchemy.orm import relationship
from .base import Base

# Association tables
user_favourite_categories = Table(
    "user_favourite_categories",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

user_registered_events = Table(
    "user_registered_events",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("event_id", ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_category_name", "name"),
        Index("ix_category_is_active", "is_active"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    events = relationship("Event", back_populates="category")
    favourited_by = relationship("User", secondary=user_favourite_categories, back_populates="favourite_categories")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_event_postal_code", "postal_code"),
        Index("ix_event_category_id", "category_id"),
        Index("ix_event_date_begin", "date_begin"),
        Index("ix_event_status", "status"),
        Index("ix_event_is_active", "is_active"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    
    # Multilingual fields
    title = Column(String, nullable=False)
    title_ar = Column(String, nullable=True)
    title_fr = Column(String, nullable=True)
    title_tam = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    description_fr = Column(Text, nullable=True)
    description_tam = Column(Text, nullable=True)
    
    # Location
    address = Column(String, nullable=False)
    postal_code = Column(String(5), nullable=False)
    commune = Column(String, nullable=False)
    wilaya = Column(String, nullable=False)
    
    # Schedule
    date_begin = Column(DateTime(timezone=True), nullable=False)
    date_end = Column(DateTime(timezone=True), nullable=True)
    
    # Capacity & registration
    capacity = Column(Integer, nullable=True)
    remaining_spots = Column(Integer, nullable=True)
    registration_link = Column(String, nullable=True)
    registration_contact = Column(String, nullable=True)
    registration_required = Column(Boolean, default=False)
    
    # Volunteering
    is_volunteering = Column(Boolean, default=False)
    volunteer_skills = Column(Text, nullable=True)
    
    # Simple cost (non-multilingual)
    cost = Column(String, default="Free")
    
    # Status
    status = Column(String, default="upcoming")
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category = relationship("Category", back_populates="events")
    registered_users = relationship("User", secondary=user_registered_events, back_populates="registered_events")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_user_email", "email"),
        Index("ix_user_username", "username"),
        Index("ix_user_is_active", "is_active"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True, index=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    
    preferred_language = Column(String, default="fr")
    postal_code = Column(String(5), nullable=True)
    
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    favourite_categories = relationship("Category", secondary=user_favourite_categories, back_populates="favourited_by")
    registered_events = relationship("Event", secondary=user_registered_events, back_populates="registered_users")


class YouthCenter(Base):
    __tablename__ = "youth_centers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    wilaya = Column(String, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    languages = Column(String, nullable=False, server_default="fr")
    is_active = Column(Boolean, nullable=False, server_default=func.true())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    programs = relationship("Program", back_populates="center")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    center_id = Column(Integer, ForeignKey("youth_centers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    language = Column(String, nullable=False)
    capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=func.true())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    center = relationship("YouthCenter", back_populates="programs")


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(String, nullable=False)
    language = Column(String, nullable=True)
    wilaya_filter = Column(String, nullable=True)
    cache_hit = Column(Boolean, nullable=False, server_default=func.false())
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_slug = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)