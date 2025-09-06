from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.db import Base

class JD(Base):
    __tablename__ = "jds"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    required_skills = Column(JSON, nullable=True)  # List of required skills
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    matches = relationship("MatchResult", back_populates="jd")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    resume_path = Column(String, nullable=False)
    extracted_skills = Column(JSON, nullable=True)  # List of extracted skills
    experience_years = Column(Integer, nullable=True)
    education = Column(String, nullable=True)
    gender = Column(String, nullable=True)  # For bias detection
    status = Column(String, default="pending")  # pending, shortlisted, rejected, accepted
    created_at = Column(DateTime, default=datetime.utcnow)
    is_shortlisted = Column(Boolean, default=False)

    matches = relationship("MatchResult", back_populates="candidate")

class MatchResult(Base):
    __tablename__ = "match_results"
    id = Column(Integer, primary_key=True, index=True)
    jd_id = Column(Integer, ForeignKey("jds.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    overall_score = Column(Float)
    skills_match_score = Column(Float)
    experience_match_score = Column(Float)
    matched_skills = Column(JSON, nullable=True)  # Skills that matched
    missing_skills = Column(JSON, nullable=True)  # Skills candidate lacks
    skill_gaps = Column(JSON, nullable=True)  # Detailed gap analysis
    created_at = Column(DateTime, default=datetime.utcnow)

    jd = relationship("JD", back_populates="matches")
    candidate = relationship("Candidate", back_populates="matches")

class BiasAlert(Base):
    __tablename__ = "bias_alerts"
    id = Column(Integer, primary_key=True, index=True)
    jd_id = Column(Integer, ForeignKey("jds.id"))
    alert_type = Column(String)  # 'gender', 'experience', 'education'
    description = Column(Text)
    severity = Column(String)  # 'low', 'medium', 'high'
    created_at = Column(DateTime, default=datetime.utcnow)

class DiversityMetrics(Base):
    __tablename__ = "diversity_metrics"
    id = Column(Integer, primary_key=True, index=True)
    jd_id = Column(Integer, ForeignKey("jds.id"))
    gender_distribution = Column(JSON)
    experience_distribution = Column(JSON)
    education_distribution = Column(JSON)
    calculated_at = Column(DateTime, default=datetime.utcnow)
