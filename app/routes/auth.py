from fastapi import APIRouter, HTTPException, Depends
from app.schemas import RegisterRequest, LoginRequest, GoogleAuthRequest, AuthResponse, UserProfile
from app.services.user_service import create_user, get_user_by_email, create_or_get_google_user
from app.services.auth_service import verify_password, create_jwt_token, verify_google_token
from app.middleware.auth import get_current_user
import re

router = APIRouter()

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    # Validate fast
    if not re.match(r"[^@]+@[^@]+\.[^@]+", req.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing_user = await get_user_by_email(req.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = await create_user(req.name, req.email, req.password)
    if not user:
        raise HTTPException(status_code=500, detail="Error creating user")

    token = create_jwt_token(str(user["id"]), user["email"])
    
    return AuthResponse(
        token=token,
        user=UserProfile(
            id=str(user["id"]),
            name=user.get("name"),
            email=user["email"],
            subscription_plan=user.get("subscription_plan", "free"),
            queries_today=user.get("queries_today", 0)
        )
    )

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    user = await get_user_by_email(req.email)
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_jwt_token(str(user["id"]), user["email"])
    
    return AuthResponse(
        token=token,
        user=UserProfile(
            id=str(user["id"]),
            name=user.get("name"),
            email=user["email"],
            subscription_plan=user.get("subscription_plan", "free"),
            queries_today=user.get("queries_today", 0)
        )
    )

@router.post("/google", response_model=AuthResponse)
async def google_auth(req: GoogleAuthRequest):
    google_data = verify_google_token(req.id_token)
    if not google_data or not google_data.get("email"):
        raise HTTPException(status_code=400, detail="Could not retrieve email from Google")
        
    user = await create_or_get_google_user(
        google_data["email"], 
        google_data.get("name", ""), 
        google_data.get("google_id", "")
    )
    if not user:
        raise HTTPException(status_code=500, detail="Error with Google Authentication")

    token = create_jwt_token(str(user["id"]), user["email"])
    
    return AuthResponse(
        token=token,
        user=UserProfile(
            id=str(user["id"]),
            name=user.get("name"),
            email=user["email"],
            subscription_plan=user.get("subscription_plan", "free"),
            queries_today=user.get("queries_today", 0)
        )
    )

from app.schemas import SupabaseAuthRequest
from app.services.auth_service import verify_supabase_token

@router.post("/supabase", response_model=AuthResponse)
async def supabase_auth(req: SupabaseAuthRequest):
    supabase_data = await verify_supabase_token(req.access_token)
    
    user = await create_or_get_google_user(
        supabase_data["email"], 
        supabase_data.get("name", ""), 
        "" 
    )
    if not user:
        raise HTTPException(status_code=500, detail="Error with Supabase Authentication")

    token = create_jwt_token(str(user["id"]), user["email"])
    
    return AuthResponse(
        token=token,
        user=UserProfile(
            id=str(user["id"]),
            name=user.get("name"),
            email=user["email"],
            subscription_plan=user.get("subscription_plan", "free"),
            queries_today=user.get("queries_today", 0)
        )
    )

@router.get("/me", response_model=UserProfile)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserProfile(
        id=str(current_user["id"]),
        name=current_user.get("name"),
        email=current_user["email"],
        subscription_plan=current_user.get("subscription_plan", "free"),
        queries_today=current_user.get("queries_today", 0)
    )

@router.post("/upgrade")
async def upgrade_plan(request: dict, current_user: dict = Depends(get_current_user)):
    """Upgrade user's subscription plan after successful Razorpay payment."""
    from app.services.user_service import update_user_plan
    from app.database import execute

    plan = request.get("plan")
    razorpay_payment_id = request.get("razorpay_payment_id") or request.get("payment_id")

    if not plan or plan not in ["basic", "pro", "medical_pro"]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    # Update user's plan in database
    await update_user_plan(current_user["id"], plan)

    # Save subscription record
    await execute(
        """INSERT INTO subscriptions (user_id, plan, razorpay_payment_id, status, started_at)
           VALUES ($1, $2, $3, 'active', NOW())""",
        current_user["id"], plan, razorpay_payment_id
    )

    return {"message": "Plan upgraded successfully", "plan": plan}
