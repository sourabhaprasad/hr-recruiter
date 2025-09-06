from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.db import get_db
from core.models import Candidate, JD, MatchResult
from services.mailer import send_rejection_email, send_shortlist_email
from datetime import datetime, timedelta
import random

router = APIRouter()

class StatusUpdate(BaseModel):
    candidate_id: int
    status: str  # pending, shortlisted, rejected, accepted

@router.patch("/status")
async def update_candidate_status(
    status_update: StatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update candidate status and send appropriate emails"""
    candidate = db.query(Candidate).filter(Candidate.id == status_update.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    valid_statuses = ["pending", "shortlisted", "rejected", "accepted"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Get job details for email context
    match_result = db.query(MatchResult).filter(MatchResult.candidate_id == candidate.id).first()
    jd = None
    if match_result:
        jd = db.query(JD).filter(JD.id == match_result.jd_id).first()
    
    old_status = candidate.status
    candidate.status = status_update.status
    # Update is_shortlisted for backward compatibility
    candidate.is_shortlisted = status_update.status == "shortlisted"
    
    db.commit()
    db.refresh(candidate)
    
    # Send emails based on status change
    if status_update.status == "rejected" and old_status != "rejected":
        # Generate rejection reason based on candidate's match data
        rejection_reasons = []
        if match_result:
            if match_result.skills_match_score < 0.5:
                rejection_reasons.append("Skills alignment did not meet the minimum requirements")
            if match_result.experience_match_score < 0.4:
                rejection_reasons.append("Experience level does not match the position requirements")
            if match_result.overall_score < 0.6:
                rejection_reasons.append("Overall profile compatibility was below our threshold")
        
        if not rejection_reasons:
            rejection_reasons = ["Profile did not align with current position requirements"]
        
        background_tasks.add_task(
            send_rejection_email,
            candidate.email,
            candidate.name,
            jd.title if jd else "the position",
            rejection_reasons
        )
    
    elif status_update.status == "shortlisted" and old_status != "shortlisted":
        # Generate random interview date (3-10 days from now)
        interview_date = datetime.now() + timedelta(days=random.randint(3, 10))
        
        background_tasks.add_task(
            send_shortlist_email,
            candidate.email,
            candidate.name,
            jd.title if jd else "the position",
            interview_date.strftime("%B %d, %Y at %I:%M %p")
        )
    
    return {
        "message": "Status updated successfully",
        "candidate_id": candidate.id,
        "new_status": candidate.status,
        "email_sent": status_update.status in ["rejected", "shortlisted"]
    }

@router.get("/statuses")
async def get_status_counts(db: Session = Depends(get_db)):
    """Get candidate status distribution"""
    from sqlalchemy import func
    
    status_counts = db.query(
        Candidate.status,
        func.count(Candidate.id).label('count')
    ).group_by(Candidate.status).all()
    
    return {
        status: count for status, count in status_counts
    }
