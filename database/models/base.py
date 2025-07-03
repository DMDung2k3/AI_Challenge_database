# database/models/base.py
from sqlalchemy.ext.declarative import declarative_base

# Base metadata for all models
template_base = declarative_base()
Base = template_base  # alias for clarity


# database/models/user_session.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from .base import Base


