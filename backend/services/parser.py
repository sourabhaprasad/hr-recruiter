import PyPDF2
import docx
import re
import json
from typing import Dict, List, Optional
import spacy

# Load spaCy model for NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if model not installed
    nlp = None

# Common skills database
COMMON_SKILLS = {
    "programming": ["python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "rust", "swift", "kotlin", "scala", "r", "matlab"],
    "web": ["html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "laravel"],
    "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "sqlite"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "git"],
    "data": ["pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "tableau", "power bi", "spark"],
    "mobile": ["android", "ios", "react native", "flutter", "xamarin"],
    "other": ["agile", "scrum", "devops", "machine learning", "artificial intelligence", "blockchain"]
}

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""

def extract_text_from_file(file_path: str) -> str:
    """Extract text from file based on extension"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_email(text: str) -> Optional[str]:
    """Extract email from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_name(text: str) -> Optional[str]:
    """Extract candidate name from text"""
    lines = text.split('\n')
    
    # Try to find name in first few lines
    for i, line in enumerate(lines[:5]):
        line = line.strip()
        if not line:
            continue
            
        # Skip lines that look like headers, emails, phones, or addresses
        if any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum', '@', 'phone', 'email', 'address', 'street', 'city']):
            continue
            
        # Skip lines with too many special characters or numbers
        if len(re.findall(r'[^a-zA-Z\s]', line)) > len(line) * 0.3:
            continue
            
        # Look for name patterns (2-4 words, mostly alphabetic)
        words = line.split()
        if 2 <= len(words) <= 4:
            # Check if words are mostly alphabetic
            if all(len(word) > 1 and word.replace('-', '').replace("'", '').isalpha() for word in words):
                # Check if it's likely a name (proper case or all caps)
                if all(word[0].isupper() for word in words):
                    return line.title()
    
    # If spaCy is available, try NER
    if nlp:
        doc = nlp(text[:1000])  # Process first 1000 chars for performance
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                return ent.text.title()
    
    return None

def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    # Multiple phone patterns to catch different formats
    phone_patterns = [
        r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'(\+\d{1,3}[-.\s]?)?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',       # Simple format
        r'(\+\d{1,3}[-.\s]?)?\d{10}',                               # 10 digits
        r'(\+\d{1,3}[-.\s]?)?\d{3}[-.\s]?\d{4}[-.\s]?\d{3}',       # Alternative format
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            # Clean up the phone number
            phone = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
            # Remove extra characters and format nicely
            digits = re.sub(r'[^\d+]', '', phone)
            if len(digits) >= 10:
                return phone.strip()
    
    return None

def extract_experience_years(text: str) -> Optional[int]:
    """Extract years of experience from text"""
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience\s*(?:of\s*)?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry)',
    ]
    
    text_lower = text.lower()
    for pattern in experience_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            return int(matches[0])
    return None

def extract_education(text: str) -> Optional[str]:
    """Extract education information from text"""
    education_keywords = [
        "bachelor", "master", "phd", "doctorate", "mba", "degree",
        "university", "college", "institute", "school"
    ]
    
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in education_keywords):
            if len(line.strip()) < 200:  # Reasonable length for education line
                return line.strip()
    return None

def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from text using keyword matching"""
    text_lower = text.lower()
    found_skills = []
    
    # Check all skill categories
    for category, skills in COMMON_SKILLS.items():
        for skill in skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
    
    # Remove duplicates and return
    return list(set(found_skills))

def extract_skills_with_nlp(text: str) -> List[str]:
    """Extract skills using NLP if spaCy is available"""
    if not nlp:
        return extract_skills_from_text(text)
    
    # Process text with spaCy
    doc = nlp(text)
    
    # Extract entities and noun phrases that might be skills
    potential_skills = []
    
    # Get named entities
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE"]:
            potential_skills.append(ent.text.lower())
    
    # Get noun phrases
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3:  # Keep short phrases
            potential_skills.append(chunk.text.lower())
    
    # Combine with keyword-based extraction
    keyword_skills = extract_skills_from_text(text)
    
    # Filter and combine results
    all_skills = keyword_skills + potential_skills
    
    # Remove duplicates and filter out common words
    common_words = {"experience", "work", "team", "project", "company", "time", "year"}
    filtered_skills = [skill for skill in set(all_skills) if skill not in common_words]
    
    return filtered_skills[:20]  # Limit to top 20 skills

def parse_resume(file_path: str) -> Dict:
    """Parse resume and extract structured information"""
    text = extract_text_from_file(file_path)
    
    if not text:
        return {"error": "Could not extract text from file"}
    
    # Extract information
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    experience_years = extract_experience_years(text)
    education = extract_education(text)
    skills = extract_skills_with_nlp(text)
    
    return {
        "raw_text": text,
        "name": name,
        "email": email,
        "phone": phone,
        "experience_years": experience_years,
        "education": education,
        "extracted_skills": skills,
        "text_length": len(text)
    }

def extract_jd_requirements(jd_text: str) -> Dict:
    """Extract requirements from job description"""
    skills = extract_skills_with_nlp(jd_text)
    experience_years = extract_experience_years(jd_text)
    education = extract_education(jd_text)
    
    return {
        "required_skills": skills,
        "required_experience": experience_years,
        "required_education": education
    }