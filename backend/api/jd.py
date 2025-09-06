from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from core.models import JD, Candidate, MatchResult
from services.parser import extract_text_from_file, extract_jd_requirements
import os
import json
import shutil

router = APIRouter()
from services.matcher import calculate_comprehensive_match
from typing import Optional

UPLOAD_DIR = "uploads/jd"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_jd(
    title: str = Form(...),
    file: UploadFile | None = None,
    text: str | None = Form(None),
    db: Session = Depends(get_db)
):
    """Upload job description and extract requirements"""
    if not file and not text:
        raise HTTPException(status_code=400, detail="Either file or text must be provided")
    
    file_path = None
    jd_text = text or ""
    
    # Handle file upload
    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text from file
        extracted_text = extract_text_from_file(file_path)
        if extracted_text:
            jd_text = extracted_text
    
    # Extract requirements from JD text
    requirements = extract_jd_requirements(jd_text)
    
    # Create JD record
    jd = JD(
        title=title,
        description=jd_text,
        file_path=file_path,
        required_skills=requirements.get("required_skills", [])
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)
    
    # Trigger matching for existing candidates
    candidates = db.query(Candidate).all()
    for candidate in candidates:
        # Get candidate data
        candidate_data = {
            "raw_text": "",
            "extracted_skills": candidate.extracted_skills or [],
            "experience_years": candidate.experience_years
        }
        
        # Extract text from resume if needed
        if candidate.resume_path and os.path.exists(candidate.resume_path):
            candidate_data["raw_text"] = extract_text_from_file(candidate.resume_path)
        
        # Calculate match
        jd_data = {
            "description": jd_text,
            "required_skills": requirements.get("required_skills", []),
            "required_experience": requirements.get("required_experience")
        }
        
        match_result = calculate_comprehensive_match(jd_data, candidate_data)
        
        # Save or update match result
        existing_match = db.query(MatchResult).filter(
            MatchResult.jd_id == jd.id,
            MatchResult.candidate_id == candidate.id
        ).first()
        
        if existing_match:
            existing_match.overall_score = match_result["overall_score"]
            existing_match.skills_match_score = match_result["skills_match_score"]
            existing_match.experience_match_score = match_result["experience_match_score"]
            existing_match.matched_skills = match_result["matched_skills"]
            existing_match.missing_skills = match_result["missing_skills"]
            existing_match.skill_gaps = match_result["skill_gaps"]
        else:
            match = MatchResult(
                jd_id=jd.id,
                candidate_id=candidate.id,
                overall_score=match_result["overall_score"],
                skills_match_score=match_result["skills_match_score"],
                experience_match_score=match_result["experience_match_score"],
                matched_skills=match_result["matched_skills"],
                missing_skills=match_result["missing_skills"],
                skill_gaps=match_result["skill_gaps"]
            )
            db.add(match)
    
    db.commit()
    
    return {
        "message": "JD uploaded successfully",
        "jd_id": jd.id,
        "extracted_requirements": requirements,
        "candidates_matched": len(candidates)
    }

@router.get("/")
def get_jds(db: Session = Depends(get_db)):
    """Get all job descriptions"""
    jds = db.query(JD).filter(JD.is_active == True).all()
    return [
        {
            "id": jd.id,
            "title": jd.title,
            "description": jd.description[:200] + "..." if len(jd.description or "") > 200 else jd.description,
            "required_skills": jd.required_skills,
            "created_at": jd.created_at
        }
        for jd in jds
    ]

@router.get("/titles/list")
def get_jd_titles(db: Session = Depends(get_db)):
    """Get job titles for dropdown"""
    jds = db.query(JD).filter(JD.is_active == True).all()
    return [
        {
            "id": jd.id,
            "title": jd.title
        }
        for jd in jds
    ]

@router.get("/{jd_id}")
def get_jd(jd_id: int, db: Session = Depends(get_db)):
    """Get specific job description"""
    jd = db.query(JD).filter(JD.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")
    
    return {
        "id": jd.id,
        "title": jd.title,
        "description": jd.description,
        "required_skills": jd.required_skills,
        "created_at": jd.created_at,
        "is_active": jd.is_active
    }
