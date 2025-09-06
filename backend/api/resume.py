from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil, os
from core.db import get_db
from core.models import Candidate, MatchResult, JD
from services.parser import parse_resume
from services.matcher import calculate_comprehensive_match
from typing import Optional

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/extract")
async def extract_resume_details(file: UploadFile):
    """Extract details from resume file for auto-filling form"""
    if not file:
        raise HTTPException(status_code=400, detail="Resume file is required")
    
    # Save temporary file
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Parse resume
        parsed_data = parse_resume(temp_path)
        
        if "error" in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data["error"])
        
        return {
            "name": parsed_data.get("name", ""),
            "email": parsed_data.get("email", ""),
            "phone": parsed_data.get("phone", ""),
            "skills": parsed_data.get("extracted_skills", []),
            "experience_years": parsed_data.get("experience_years"),
            "education": parsed_data.get("education", "")
        }
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/upload")
async def upload_resume(
    name: str = Form(...),
    jd_id: int = Form(...),
    email: str = Form(None),
    phone: str = Form(None),
    gender: str = Form(None),
    file: UploadFile = None,
    db: Session = Depends(get_db)
):
    """Upload resume and extract candidate information"""
    if not file:
        raise HTTPException(status_code=400, detail="Resume file is required")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Parse resume
    parsed_data = parse_resume(file_path)
    
    if "error" in parsed_data:
        raise HTTPException(status_code=400, detail=parsed_data["error"])
    
    # Create candidate record with extracted data
    candidate = Candidate(
        name=name,
        email=email or parsed_data.get("email"),
        phone=phone or parsed_data.get("phone"),
        gender=gender,
        resume_path=file_path,
        extracted_skills=parsed_data.get("extracted_skills", []),
        experience_years=parsed_data.get("experience_years"),
        education=parsed_data.get("education")
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    
    # Match against the specific JD only
    jd = db.query(JD).filter(JD.id == jd_id, JD.is_active == True).first()
    matches_created = 0
    
    if jd:
        # Prepare data for matching
        jd_data = {
            "description": jd.description or "",
            "required_skills": jd.required_skills or [],
            "required_experience": None  # Could be extracted from JD in future
        }
        
        candidate_data = {
            "raw_text": parsed_data.get("raw_text", ""),
            "extracted_skills": parsed_data.get("extracted_skills", []),
            "experience_years": parsed_data.get("experience_years")
        }
        
        # Calculate comprehensive match
        match_result = calculate_comprehensive_match(jd_data, candidate_data)
        
        # Create match record
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
        matches_created = 1
    
    db.commit()
    
    return {
        "message": "Resume uploaded successfully",
        "candidate_id": candidate.id,
        "extracted_data": {
            "skills": parsed_data.get("extracted_skills", []),
            "experience_years": parsed_data.get("experience_years"),
            "education": parsed_data.get("education"),
            "email": candidate.email,
            "phone": candidate.phone
        },
        "matches_created": matches_created
    }

@router.get("/")
def get_candidates(db: Session = Depends(get_db)):
    """Get all candidates"""
    candidates = db.query(Candidate).all()
    return [
        {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "extracted_skills": candidate.extracted_skills,
            "experience_years": candidate.experience_years,
            "education": candidate.education,
            "gender": candidate.gender,
            "created_at": candidate.created_at,
            "is_shortlisted": candidate.is_shortlisted
        }
        for candidate in candidates
    ]

@router.get("/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get specific candidate details"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get match results for this candidate
    matches = db.query(MatchResult).filter(MatchResult.candidate_id == candidate_id).all()
    match_data = []
    
    for match in matches:
        jd = db.query(JD).filter(JD.id == match.jd_id).first()
        match_data.append({
            "jd_id": match.jd_id,
            "jd_title": jd.title if jd else "Unknown",
            "overall_score": match.overall_score,
            "skills_match_score": match.skills_match_score,
            "experience_match_score": match.experience_match_score,
            "matched_skills": match.matched_skills,
            "missing_skills": match.missing_skills,
            "skill_gaps": match.skill_gaps
        })
    
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "extracted_skills": candidate.extracted_skills,
        "experience_years": candidate.experience_years,
        "education": candidate.education,
        "gender": candidate.gender,
        "created_at": candidate.created_at,
        "is_shortlisted": candidate.is_shortlisted,
        "matches": match_data
    }
