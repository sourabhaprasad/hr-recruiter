import random
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from services.parser import extract_skills_with_nlp, extract_experience_years

def calculate_skills_match(jd_skills: List[str], candidate_skills: List[str]) -> Dict:
    """Calculate skill matching score with generalized matching and identify gaps"""
    if not jd_skills or not candidate_skills:
        return {
            "score": 0.0,
            "matched_skills": [],
            "missing_skills": jd_skills or [],
            "skill_gaps": []
        }
    
    # Skill synonyms and related terms for better matching
    skill_synonyms = {
        "javascript": ["js", "node.js", "nodejs", "react", "vue", "angular"],
        "python": ["django", "flask", "fastapi", "pandas", "numpy"],
        "java": ["spring", "hibernate", "maven", "gradle"],
        "database": ["sql", "mysql", "postgresql", "mongodb", "nosql"],
        "web development": ["html", "css", "frontend", "backend", "full stack"],
        "machine learning": ["ml", "ai", "deep learning", "tensorflow", "pytorch"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
        "project management": ["agile", "scrum", "kanban", "jira"],
        "data analysis": ["analytics", "statistics", "excel", "tableau", "powerbi"],
        "mobile": ["android", "ios", "react native", "flutter"]
    }
    
    # Convert to lowercase and normalize
    jd_skills_lower = [skill.lower().strip() for skill in jd_skills]
    candidate_skills_lower = [skill.lower().strip() for skill in candidate_skills]
    
    # Find exact and fuzzy matches
    matched_skills = []
    match_scores = []
    
    for jd_skill in jd_skills_lower:
        best_match_score = 0.0
        best_match = None
        
        # Check exact match first
        if jd_skill in candidate_skills_lower:
            matched_skills.append(jd_skill)
            match_scores.append(1.0)
            continue
        
        # Check partial matches and synonyms
        for candidate_skill in candidate_skills_lower:
            score = 0.0
            
            # Partial string matching
            if jd_skill in candidate_skill or candidate_skill in jd_skill:
                score = max(score, 0.8)
            
            # Check synonyms
            for base_skill, synonyms in skill_synonyms.items():
                if jd_skill == base_skill or jd_skill in synonyms:
                    if candidate_skill == base_skill or candidate_skill in synonyms:
                        score = max(score, 0.9)
                elif candidate_skill == base_skill or candidate_skill in synonyms:
                    if jd_skill == base_skill or jd_skill in synonyms:
                        score = max(score, 0.9)
            
            # Word similarity for compound skills
            jd_words = set(jd_skill.split())
            candidate_words = set(candidate_skill.split())
            if jd_words and candidate_words:
                common_words = jd_words.intersection(candidate_words)
                if common_words:
                    similarity = len(common_words) / max(len(jd_words), len(candidate_words))
                    if similarity >= 0.5:
                        score = max(score, similarity * 0.7)
            
            if score > best_match_score:
                best_match_score = score
                best_match = candidate_skill
        
        # Accept matches with score >= 0.6
        if best_match_score >= 0.6:
            matched_skills.append(jd_skill)
            match_scores.append(best_match_score)
    
    # Calculate weighted score based on match quality
    if len(jd_skills_lower) == 0:
        score = 1.0
    else:
        weighted_score = sum(match_scores) / len(jd_skills_lower)
        score = min(weighted_score, 1.0)  # Cap at 1.0
    
    # Find missing skills (those not matched)
    missing_skills = [skill for i, skill in enumerate(jd_skills_lower) 
                     if i >= len(match_scores) or (i < len(match_scores) and match_scores[i] < 0.6)]
    
    # Generate skill gaps with suggestions
    skill_gaps = []
    for missing_skill in missing_skills:
        gap = {
            "skill": missing_skill,
            "importance": "high" if missing_skill in jd_skills_lower[:5] else "medium",
            "suggestion": f"Consider learning {missing_skill}"
        }
        skill_gaps.append(gap)
    
    return {
        "score": round(score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_gaps": skill_gaps
    }

def calculate_experience_match(required_exp: int, candidate_exp: int) -> float:
    """Calculate experience matching score"""
    if required_exp is None or candidate_exp is None:
        return 0.5  # Neutral score when experience is unknown
    
    if candidate_exp >= required_exp:
        return 1.0
    elif candidate_exp >= required_exp * 0.8:
        return 0.8
    elif candidate_exp >= required_exp * 0.6:
        return 0.6
    elif candidate_exp >= required_exp * 0.4:
        return 0.4
    else:
        return 0.2

def calculate_text_similarity(jd_text: str, resume_text: str) -> float:
    """Calculate text similarity using TF-IDF and cosine similarity"""
    try:
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Fit and transform texts
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        return round(float(similarity[0][0]), 2)
    except Exception as e:
        print(f"Error calculating text similarity: {e}")
        return 0.5

def calculate_comprehensive_match(jd_data: Dict, candidate_data: Dict) -> Dict:
    """Calculate comprehensive matching score with detailed breakdown"""
    
    # Extract data
    jd_text = jd_data.get("description", "")
    jd_skills = jd_data.get("required_skills", [])
    jd_experience = jd_data.get("required_experience")
    
    resume_text = candidate_data.get("raw_text", "")
    candidate_skills = candidate_data.get("extracted_skills", [])
    candidate_experience = candidate_data.get("experience_years")
    
    # Calculate individual scores
    skills_match = calculate_skills_match(jd_skills, candidate_skills)
    experience_score = calculate_experience_match(jd_experience, candidate_experience)
    text_similarity = calculate_text_similarity(jd_text, resume_text)
    
    # Weighted overall score
    weights = {
        "skills": 0.5,
        "experience": 0.3,
        "text_similarity": 0.2
    }
    
    overall_score = (
        skills_match["score"] * weights["skills"] +
        experience_score * weights["experience"] +
        text_similarity * weights["text_similarity"]
    )
    
    return {
        "overall_score": round(overall_score, 2),
        "skills_match_score": skills_match["score"],
        "experience_match_score": experience_score,
        "text_similarity_score": text_similarity,
        "matched_skills": skills_match["matched_skills"],
        "missing_skills": skills_match["missing_skills"],
        "skill_gaps": skills_match["skill_gaps"],
        "breakdown": {
            "skills_weight": weights["skills"],
            "experience_weight": weights["experience"],
            "text_similarity_weight": weights["text_similarity"]
        }
    }

def calculate_match_score(jd_text: str, resume_text: str) -> float:
    """Legacy function for backward compatibility"""
    return calculate_text_similarity(jd_text, resume_text)

def detect_bias_in_candidates(candidates: List[Dict]) -> List[Dict]:
    """Detect potential bias in candidate selection"""
    alerts = []
    
    if len(candidates) < 3:
        return alerts
    
    # Check gender distribution in top candidates
    top_candidates = sorted(candidates, key=lambda x: x.get("overall_score", 0), reverse=True)[:5]
    genders = [c.get("gender") for c in top_candidates if c.get("gender")]
    
    if genders:
        gender_counts = {}
        for gender in genders:
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        # Check if one gender dominates (>80%)
        total = len(genders)
        for gender, count in gender_counts.items():
            if count / total > 0.8:
                alerts.append({
                    "type": "gender",
                    "description": f"Top candidates are {count/total*100:.0f}% {gender}",
                    "severity": "high" if count / total > 0.9 else "medium"
                })
    
    # Check experience distribution
    experiences = [c.get("experience_years") for c in top_candidates if c.get("experience_years")]
    if experiences:
        avg_exp = sum(experiences) / len(experiences)
        if avg_exp > 10:
            alerts.append({
                "type": "experience",
                "description": f"Top candidates have high average experience ({avg_exp:.1f} years)",
                "severity": "medium"
            })
        elif avg_exp < 2:
            alerts.append({
                "type": "experience", 
                "description": f"Top candidates have low average experience ({avg_exp:.1f} years)",
                "severity": "medium"
            })
    
    return alerts

def calculate_diversity_metrics(candidates: List[Dict]) -> Dict:
    """Calculate diversity metrics for candidates"""
    if not candidates:
        return {}
    
    # Gender distribution
    genders = [c.get("gender") for c in candidates if c.get("gender")]
    gender_dist = {}
    if genders:
        for gender in genders:
            gender_dist[gender] = gender_dist.get(gender, 0) + 1
        # Convert to percentages
        total = len(genders)
        gender_dist = {k: round(v/total*100, 1) for k, v in gender_dist.items()}
    
    # Experience distribution
    experiences = [c.get("experience_years") for c in candidates if c.get("experience_years")]
    exp_dist = {"0-2": 0, "3-5": 0, "6-10": 0, "10+": 0}
    if experiences:
        for exp in experiences:
            if exp <= 2:
                exp_dist["0-2"] += 1
            elif exp <= 5:
                exp_dist["3-5"] += 1
            elif exp <= 10:
                exp_dist["6-10"] += 1
            else:
                exp_dist["10+"] += 1
        # Convert to percentages
        total = len(experiences)
        exp_dist = {k: round(v/total*100, 1) for k, v in exp_dist.items()}
    
    # Education distribution (simplified)
    educations = [c.get("education") for c in candidates if c.get("education")]
    edu_dist = {}
    if educations:
        for edu in educations:
            edu_lower = edu.lower()
            if "bachelor" in edu_lower:
                key = "Bachelor's"
            elif "master" in edu_lower:
                key = "Master's"
            elif "phd" in edu_lower or "doctorate" in edu_lower:
                key = "PhD"
            else:
                key = "Other"
            edu_dist[key] = edu_dist.get(key, 0) + 1
        # Convert to percentages
        total = len(educations)
        edu_dist = {k: round(v/total*100, 1) for k, v in edu_dist.items()}
    
    return {
        "gender_distribution": gender_dist,
        "experience_distribution": exp_dist,
        "education_distribution": edu_dist
    }
