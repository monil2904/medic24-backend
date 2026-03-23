import uuid
from app.database import fetch_one, execute
from app.services.auth_service import hash_password

async def create_user(name: str, email: str, password: str) -> dict | None:
    hashed_pwd = hash_password(password)
    query = """
    INSERT INTO users (name, email, password_hash, subscription_plan, queries_today, created_at)
    VALUES ($1, $2, $3, 'free', 0, NOW())
    RETURNING id, name, email, password_hash, google_id, subscription_plan, queries_today, created_at
    """
    record = await fetch_one(query, name, email, hashed_pwd)
    return dict(record) if record else None

async def get_user_by_email(email: str) -> dict | None:
    query = "SELECT * FROM users WHERE email = $1"
    record = await fetch_one(query, email)
    return dict(record) if record else None

async def get_user_by_id(user_id: str) -> dict | None:
    query = "SELECT * FROM users WHERE id = $1::uuid"
    record = await fetch_one(query, user_id)
    return dict(record) if record else None

async def create_or_get_google_user(email: str, name: str, google_id: str) -> dict | None:
    query = """
    INSERT INTO users (name, email, google_id, subscription_plan, queries_today, created_at)
    VALUES ($1, $2, $3, 'free', 0, NOW())
    ON CONFLICT (email) DO UPDATE 
        SET google_id = EXCLUDED.google_id
    RETURNING id, name, email, password_hash, google_id, subscription_plan, queries_today, created_at
    """
    record = await fetch_one(query, name, email, google_id)
    return dict(record) if record else None

async def update_user_plan(user_id: str, plan: str) -> None:
    query = "UPDATE users SET subscription_plan = $1 WHERE id = $2::uuid"
    await execute(query, plan, user_id)

async def increment_queries(user_id: str) -> int:
    """Increment daily query count. Reset if it's a new day."""
    from datetime import datetime, timezone

    user = await fetch_one("SELECT queries_today, queries_reset_at FROM users WHERE id = $1::uuid", user_id)
    if not user:
        return 0

    now = datetime.now(timezone.utc)
    last_reset = user["queries_reset_at"]

    # If last reset was on a different day, reset counter
    if last_reset is None or last_reset.date() < now.date():
        await execute(
            "UPDATE users SET queries_today = 1, queries_reset_at = $1 WHERE id = $2::uuid",
            now, user_id
        )
        return 1
    else:
        new_count = user["queries_today"] + 1
        await execute(
            "UPDATE users SET queries_today = $1 WHERE id = $2::uuid",
            new_count, user_id
        )
        return new_count

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

async def increment_image_queries(user_id: str) -> int:
    """Increment monthly image query count. Reset if new month."""
    from datetime import datetime, timezone
    user = await fetch_one("SELECT image_queries_month, month_reset_at FROM users WHERE id = $1::uuid", user_id)
    now = datetime.now(timezone.utc)

    if user["month_reset_at"] is None or user["month_reset_at"].month < now.month or user["month_reset_at"].year < now.year:
        await execute("UPDATE users SET image_queries_month = 1, month_reset_at = $1 WHERE id = $2::uuid", now, user_id)
        return 1
    else:
        new_count = user["image_queries_month"] + 1
        await execute("UPDATE users SET image_queries_month = $1 WHERE id = $2::uuid", new_count, user_id)
        return new_count

async def increment_lab_reports(user_id: str) -> int:
    """Increment monthly lab report count. Reset if new month."""
    from datetime import datetime, timezone
    user = await fetch_one("SELECT lab_reports_month, month_reset_at FROM users WHERE id = $1::uuid", user_id)
    now = datetime.now(timezone.utc)

    if user["month_reset_at"] is None or user["month_reset_at"].month < now.month or user["month_reset_at"].year < now.year:
        await execute("UPDATE users SET lab_reports_month = 1, month_reset_at = $1 WHERE id = $2::uuid", now, user_id)
        return 1
    else:
        new_count = user["lab_reports_month"] + 1
        await execute("UPDATE users SET lab_reports_month = $1 WHERE id = $2::uuid", new_count, user_id)
        return new_count
