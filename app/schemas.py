from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Auth schemas
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str

class UserProfile(BaseModel):
    id: str
    name: Optional[str]
    email: str
    subscription_plan: str
    queries_today: int

class AuthResponse(BaseModel):
    token: str
    user: UserProfile

# Chat schemas
class ChatMessage(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    message: str
    query_type: str = "general"
    include_individual: bool = False
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    ensemble_response: str
    confidence: float
    models_used: List[str]
    processing_time_ms: int
    disclaimer: str
    is_emergency: bool
    individual_responses: Optional[Dict[str, str]] = None

# Lab Report schemas
class LabReportTest(BaseModel):
    test: str
    value: float
    unit: str
    range: str
    flag: str

class LabReportResponse(BaseModel):
    parsed_results: List[LabReportTest]
    ensemble_interpretation: str
    summary: str
    abnormal_count: int
    total_tests: int
    confidence: float
