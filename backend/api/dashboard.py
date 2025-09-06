from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from core.db import get_db
from core.models import Candidate, MatchResult, JD, BiasAlert, DiversityMetrics
from services.mailer import send_shortlist_email
from typing import Optional, List
import random
from collections import Counter
import math

def calculate_actual_diversity_score(diversity_metrics: dict) -> float:
    """Calculate diversity score based on actual distribution data"""
    if not diversity_metrics:
        return 75.0
    
    # Calculate gender diversity (Shannon entropy)
    gender_dist = diversity_metrics.get("gender_distribution", {})
    gender_entropy = 0
    if gender_dist:
        for percentage in gender_dist.values():
            if percentage > 0:
                p = percentage / 100.0  # Convert percentage to probability
                gender_entropy += -p * math.log2(p)
    
    # Calculate experience diversity
    exp_dist = diversity_metrics.get("experience_distribution", {})
    exp_entropy = 0
    if exp_dist:
        for percentage in exp_dist.values():
            if percentage > 0:
                p = percentage / 100.0
                exp_entropy += -p * math.log2(p)
    
    # Calculate education diversity
    edu_dist = diversity_metrics.get("education_distribution", {})
    edu_entropy = 0
    if edu_dist:
        for percentage in edu_dist.values():
            if percentage > 0:
                p = percentage / 100.0
                edu_entropy += -p * math.log2(p)
    
    # Normalize entropies to 0-100 scale
    max_gender_entropy = math.log2(len(gender_dist)) if gender_dist else 1
    max_exp_entropy = math.log2(len(exp_dist)) if exp_dist else 1
    max_edu_entropy = math.log2(len(edu_dist)) if edu_dist else 1
    
    gender_score = (gender_entropy / max_gender_entropy * 100) if max_gender_entropy > 0 else 0
    exp_score = (exp_entropy / max_exp_entropy * 100) if max_exp_entropy > 0 else 0
    edu_score = (edu_entropy / max_edu_entropy * 100) if max_edu_entropy > 0 else 0
    
    # Weighted average (gender 40%, experience 35%, education 25%)
    diversity_score = (gender_score * 0.4 + exp_score * 0.35 + edu_score * 0.25)
    
    return round(diversity_score, 1)

def detect_bias_in_candidates(candidates: List[dict]) -> List[dict]:
    """Detect potential bias in candidate data"""
    alerts = []
    
    if not candidates:
        return alerts
    
    # Check gender distribution
    gender_counts = {}
    for candidate in candidates:
        gender = candidate.get("gender", "unknown")
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
    
    total_candidates = len(candidates)
    for gender, count in gender_counts.items():
        percentage = (count / total_candidates) * 100
        if percentage < 20 and total_candidates > 5:  # Less than 20% representation
            alerts.append({
                "type": "gender",
                "description": f"Low representation of {gender} candidates ({percentage:.1f}%)",
                "severity": "medium" if percentage < 10 else "low"
            })
    
    # Check experience distribution
    experience_counts = {}
    for candidate in candidates:
        exp = candidate.get("experience_years")
        if exp is None:
            exp_range = "unknown"
        elif exp < 2:
            exp_range = "0-2 years"
        elif exp < 5:
            exp_range = "2-5 years"
        elif exp < 10:
            exp_range = "5-10 years"
        else:
            exp_range = "10+ years"
        experience_counts[exp_range] = experience_counts.get(exp_range, 0) + 1
    
    # Check for age bias (if experience is very high)
    high_exp_count = sum(1 for c in candidates if c.get("experience_years") is not None and c.get("experience_years") > 15)
    if high_exp_count > total_candidates * 0.8:
        alerts.append({
            "type": "experience",
            "description": f"High concentration of senior candidates ({high_exp_count}/{total_candidates})",
            "severity": "medium"
        })
    
    return alerts

def calculate_diversity_metrics(candidates: List[dict]) -> dict:
    """Calculate diversity metrics for candidates"""
    if not candidates:
        return {}
    
    total_candidates = len(candidates)
    
    # Gender distribution
    gender_counts = {}
    for candidate in candidates:
        gender = candidate.get("gender", "unknown")
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
    
    gender_distribution = {gender: round((count/total_candidates) * 100, 1) for gender, count in gender_counts.items()}
    
    # Experience distribution
    experience_ranges = {"0-2": 0, "2-5": 0, "5-10": 0, "10+": 0, "unknown": 0}
    for candidate in candidates:
        exp = candidate.get("experience_years")
        if exp is None:
            experience_ranges["unknown"] += 1
        elif exp < 2:
            experience_ranges["0-2"] += 1
        elif exp < 5:
            experience_ranges["2-5"] += 1
        elif exp < 10:
            experience_ranges["5-10"] += 1
        else:
            experience_ranges["10+"] += 1
    
    experience_distribution = {range_name: round((count/total_candidates) * 100, 1) for range_name, count in experience_ranges.items()}
    
    # Education distribution
    education_counts = {}
    for candidate in candidates:
        education = candidate.get("education", "unknown")
        education_counts[education] = education_counts.get(education, 0) + 1
    
    education_distribution = {edu: round((count/total_candidates) * 100, 1) for edu, count in education_counts.items()}
    
    return {
        "gender_distribution": gender_distribution,
        "experience_distribution": experience_distribution,
        "education_distribution": education_distribution,
        "total_candidates": total_candidates
    }

def _get_candidates_data(jd_id: Optional[int] = None, db: Session = None):
    """Helper function to get candidates data"""
    if db is None:
        from core.db import get_db
        db = next(get_db())
    
    query = db.query(MatchResult, Candidate, JD).join(
        Candidate, MatchResult.candidate_id == Candidate.id
    ).join(
        JD, MatchResult.jd_id == JD.id
    )
    
    if jd_id:
        query = query.filter(MatchResult.jd_id == jd_id)
    
    results = query.filter(MatchResult.overall_score.isnot(None)).order_by(desc(MatchResult.overall_score)).all()
    
    candidates_data = []
    for match, candidate, jd in results:
        candidates_data.append({
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "overall_score": match.overall_score,
            "skills_match_score": match.skills_match_score,
            "experience_match_score": match.experience_match_score,
            "matched_skills": match.matched_skills,
            "missing_skills": match.missing_skills,
            "skill_gaps": match.skill_gaps,
            "experience_years": candidate.experience_years,
            "education": candidate.education,
            "gender": candidate.gender,
            "status": candidate.status,
            "is_shortlisted": candidate.is_shortlisted,
            "jd_id": jd.id,
            "jd_title": jd.title,
            "created_at": candidate.created_at
        })
    
    return candidates_data

router = APIRouter()

@router.get("/candidates")
def get_candidates(jd_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get ranked candidates for a specific JD or all JDs"""
    return _get_candidates_data(jd_id, db)

@router.get("/bias-alerts")
def get_bias_alerts(jd_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get bias alerts for candidates"""
    # Get candidates data
    candidates = _get_candidates_data(jd_id, db)
    
    # Detect bias
    alerts = detect_bias_in_candidates(candidates)
    
    # Save alerts to database
    if jd_id and alerts:
        # Clear existing alerts for this JD
        db.query(BiasAlert).filter(BiasAlert.jd_id == jd_id).delete()
        
        for alert in alerts:
            bias_alert = BiasAlert(
                jd_id=jd_id,
                alert_type=alert["type"],
                description=alert["description"],
                severity=alert["severity"]
            )
            db.add(bias_alert)
        db.commit()
    
    return alerts

@router.get("/diversity-metrics")
def get_diversity_metrics(jd_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get diversity metrics for candidates"""
    candidates = _get_candidates_data(jd_id, db)
    metrics = calculate_diversity_metrics(candidates)
    
    # Save metrics to database
    if jd_id and metrics:
        # Clear existing metrics for this JD
        db.query(DiversityMetrics).filter(DiversityMetrics.jd_id == jd_id).delete()
        
        diversity_record = DiversityMetrics(
            jd_id=jd_id,
            gender_distribution=metrics.get("gender_distribution", {}),
            experience_distribution=metrics.get("experience_distribution", {}),
            education_distribution=metrics.get("education_distribution", {})
        )
        db.add(diversity_record)
        db.commit()
    
    return metrics

@router.get("/skills-heatmap")
def get_skills_heatmap(jd_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get skills heatmap data showing skill gaps"""
    # Mock data for now - in a real implementation, this would analyze actual skill gaps
    skills_data = [
        {"skill": "Python", "gap": 0.3, "demand": 0.8, "supply": 0.5},
        {"skill": "JavaScript", "gap": 0.2, "demand": 0.7, "supply": 0.5},
        {"skill": "Machine Learning", "gap": 0.8, "demand": 0.9, "supply": 0.1},
        {"skill": "React", "gap": 0.4, "demand": 0.6, "supply": 0.2},
        {"skill": "SQL", "gap": 0.1, "demand": 0.5, "supply": 0.4},
        {"skill": "AWS", "gap": 0.6, "demand": 0.8, "supply": 0.2},
        {"skill": "Docker", "gap": 0.5, "demand": 0.7, "supply": 0.2},
        {"skill": "Git", "gap": 0.1, "demand": 0.4, "supply": 0.3},
    ]
    
    return {
        "skills": skills_data,
        "total_skills": len(skills_data),
        "critical_gaps": len([s for s in skills_data if s["gap"] > 0.7])
    }

@router.get("/insights")
def get_dashboard_insights(jd_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get comprehensive dashboard insights"""
    try:
        candidates = _get_candidates_data(jd_id, db)
        bias_alerts = detect_bias_in_candidates(candidates)
        diversity_metrics = calculate_diversity_metrics(candidates)
        
        # Generate risk heatmap data (mock data for now)
        heatmap_response = get_skills_heatmap(jd_id, db)
        critical_skills = [skill for skill in heatmap_response["skills"] if skill["gap"] > 0.7]
        
        # Generate risk heatmap data for departments (mock data)
        risk_heatmap = {
            "Engineering": random.randint(10, 30),
            "Marketing": random.randint(5, 25),
            "Sales": random.randint(15, 35),
            "HR": random.randint(8, 20),
            "Finance": random.randint(12, 28)
        }
        
        # Calculate diversity score based on actual data
        diversity_score = calculate_actual_diversity_score(diversity_metrics)
        
        # Generate sentiment data (mock)
        sentiment_data = {
            "positive": random.randint(60, 80),
            "neutral": random.randint(15, 25),
            "negative": random.randint(5, 15)
        }
        
        # Handle empty candidates list gracefully
        shortlisted_count = len([c for c in candidates if c.get("is_shortlisted", False)]) if candidates else 0
        average_score = round(sum(c.get("overall_score", 0) for c in candidates) / len(candidates), 2) if candidates else 0
        
        return {
            "total_candidates": len(candidates),
            "shortlisted_candidates": shortlisted_count,
            "average_score": average_score,
            "bias_alerts": bias_alerts,
            "diversity_metrics": diversity_metrics,
            "risk_heatmap": risk_heatmap,
            "diversity_score": diversity_score,
            "sentiment_data": sentiment_data,
            "top_skills": _get_top_skills(candidates),
            "skill_gaps": _get_common_skill_gaps(candidates)
        }
    except Exception as e:
        # Return a basic response if there's an error
        return {
            "total_candidates": 0,
            "shortlisted_candidates": 0,
            "average_score": 0,
            "bias_alerts": [],
            "diversity_metrics": {},
            "risk_heatmap": {"skills": [], "total_skills": 0, "critical_gaps": 0},
            "diversity_score": 0.75,
            "sentiment_data": {"positive": 70, "neutral": 20, "negative": 10},
            "top_skills": [],
            "skill_gaps": [],
            "error": str(e)
        }

def _get_top_skills(candidates: List[dict]) -> List[dict]:
    """Get most common skills across candidates"""
    skill_counts = {}
    for candidate in candidates:
        for skill in candidate.get("matched_skills", []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Sort by frequency and return top 10
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"skill": skill, "count": count} for skill, count in sorted_skills]

def _get_common_skill_gaps(candidates: List[dict]) -> List[dict]:
    """Get most common skill gaps"""
    gap_counts = {}
    for candidate in candidates:
        for skill in candidate.get("missing_skills", []):
            gap_counts[skill] = gap_counts.get(skill, 0) + 1
    
    # Sort by frequency and return top 10
    sorted_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"skill": skill, "count": count} for skill, count in sorted_gaps]

@router.post("/shortlist")
async def shortlist_candidates(
    candidate_ids: List[int],
    jd_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Shortlist candidates and send notifications"""
    # Get JD details
    jd = db.query(JD).filter(JD.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Get candidates
    candidates = db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")
    
    shortlisted_count = 0
    email_tasks = []
    
    for candidate in candidates:
        if not candidate.is_shortlisted:
            candidate.is_shortlisted = True
            candidate.status = "shortlisted"  # Update status field as well
            shortlisted_count += 1
            
            # Add email task to background
            if candidate.email:
                from datetime import datetime, timedelta
                import random
                # Generate random interview date (3-10 days from now)
                interview_date = datetime.now() + timedelta(days=random.randint(3, 10))
                
                background_tasks.add_task(
                    send_shortlist_email,
                    candidate.email,
                    candidate.name,
                    jd.title,
                    interview_date.strftime("%B %d, %Y at %I:%M %p")
                )
    
    db.commit()
    
    return {
        "message": f"Successfully shortlisted {shortlisted_count} candidates",
        "shortlisted_candidates": shortlisted_count,
        "email_notifications": len([c for c in candidates if c.email])
    }

@router.get("/candidate/{candidate_id}/details")
def get_candidate_details(candidate_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get all matches for this candidate
    matches = db.query(MatchResult, JD).join(
        JD, MatchResult.jd_id == JD.id
    ).filter(MatchResult.candidate_id == candidate_id).all()
    
    match_details = []
    for match, jd in matches:
        match_details.append({
            "jd_id": jd.id,
            "jd_title": jd.title,
            "overall_score": match.overall_score,
            "skills_match_score": match.skills_match_score,
            "experience_match_score": match.experience_match_score,
            "matched_skills": match.matched_skills,
            "missing_skills": match.missing_skills,
            "skill_gaps": match.skill_gaps
        })
    
    return {
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "extracted_skills": candidate.extracted_skills,
            "experience_years": candidate.experience_years,
            "education": candidate.education,
            "gender": candidate.gender,
            "is_shortlisted": candidate.is_shortlisted,
            "created_at": candidate.created_at
        },
        "matches": match_details
    }
