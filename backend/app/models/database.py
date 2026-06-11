from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    filename = Column(String)
    content_text = Column(Text)
    cv_score = Column(Float, default=0)
    ats_score = Column(Float, default=0)
    skill_score = Column(Float, default=0)
    employability_score = Column(Float, default=0)
    analysis_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(Text)
    requirements = Column(JSON, default=dict)
    salary_range = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    source = Column(String)
    url = Column(String)
    posted_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    job_id = Column(Integer)
    match_percentage = Column(Float)
    skill_gap_score = Column(Float)
    interview_readiness = Column(Float)
    missing_skills = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())