import uuid
from app.database import fetch_one, execute
from app.services.auth_service import hash_password

async def create_user(name: str, email: str, password: str) -> dict | None:
    hashed_pwd = hash_password(password)
    user_id = str(uuid.uuid4())
    query = """
    INSERT INTO users (id, name, email, password, subscription_plan, queries_today, created_at)
    VALUES ($1, $2, $3, $4, 'free', 0, NOW())
    RETURNING id, name, email, password, google_id, subscription_plan, queries_today, created_at
    """
    record = await fetch_one(query, user_id, name, email, hashed_pwd)
    return dict(record) if record else None

async def get_user_by_email(email: str) -> dict | None:
    query = "SELECT * FROM users WHERE email = $1"
    record = await fetch_one(query, email)
    return dict(record) if record else None

async def get_user_by_id(user_id: str) -> dict | None:
    query = "SELECT * FROM users WHERE id = $1"
    record = await fetch_one(query, user_id)
    return dict(record) if record else None

async def create_or_get_google_user(email: str, name: str, google_id: str) -> dict | None:
    user = await get_user_by_email(email)
    if user:
        # Return existing user (either created by Google before, or standard registration)
        return user
    
    user_id = str(uuid.uuid4())
    query = """
    INSERT INTO users (id, name, email, google_id, subscription_plan, queries_today, created_at)
    VALUES ($1, $2, $3, $4, 'free', 0, NOW())
    RETURNING id, name, email, password, google_id, subscription_plan, queries_today, created_at
    """
    record = await fetch_one(query, user_id, name, email, google_id)
    return dict(record) if record else None

async def update_user_plan(user_id: str, plan: str) -> None:
    query = "UPDATE users SET subscription_plan = $1 WHERE id = $2"
    await execute(query, plan, user_id)

async def increment_queries(user_id: str) -> int:
    # If the user queried today, increment it.
    # Otherwise, if last query was yesterday (or before), we reset it to 1.
    query = """
    UPDATE users 
    SET queries_today = CASE 
            WHEN DATE(last_query_date) = CURRENT_DATE THEN queries_today + 1 
            ELSE 1 
        END,
        last_query_date = NOW()
    WHERE id = $1 
    RETURNING queries_today
    """
    record = await fetch_one(query, user_id)
    return record['queries_today'] if record else 0

async def check_rate_limit(user_id: str) -> dict:
    user = await get_user_by_id(user_id)
    if not user:
        return {"allowed": False, "remaining": 0, "plan": "unknown", "limit": 0}
        
    plan = user.get("subscription_plan", "free")
    queries_today = user.get("queries_today", 0)
    
    # Custom plan limits
    limit = 10 if plan == "free" else 100
    
    allowed = queries_today < limit
    remaining = max(0, limit - queries_today)
    
    return {
        "allowed": allowed,
        "remaining": remaining,
        "plan": plan,
        "limit": limit
    }
