from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from core.db import get_db
from services.ai_assistant import ai_assistant

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

class ChatRequest(BaseModel):
    message: str
    jd_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str]

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with AI assistant about dashboard data"""
    try:
        # Get dashboard context
        context = ai_assistant.get_dashboard_context(db, request.jd_id)
        
        # Generate AI response
        response = ai_assistant.generate_response(request.message, context)
        
        # Get suggested questions
        suggestions = ai_assistant.get_suggested_questions(context)
        
        return ChatResponse(
            response=response,
            suggestions=suggestions
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Assistant error: {str(e)}")

@router.get("/suggestions")
async def get_suggestions(
    jd_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get suggested questions for the AI assistant"""
    try:
        context = ai_assistant.get_dashboard_context(db, jd_id)
        suggestions = ai_assistant.get_suggested_questions(context)
        return {"suggestions": suggestions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")

@router.get("/status")
async def get_ai_status():
    """Check if AI assistant is properly configured"""
    return {
        "configured": ai_assistant.model is not None,
        "message": "AI Assistant is ready" if ai_assistant.model else "Please configure GEMINI_API_KEY"
    }
