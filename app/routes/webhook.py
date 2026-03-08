import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException
from app.config import settings
from app.database import execute

router = APIRouter()

@router.post("/webhook")
async def razorpay_webhook(request: Request):
    """Verify and process Razorpay payment webhooks."""
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # Verify webhook signature
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = await request.json()
    event = payload.get("event", "")

    if event == "payment.captured":
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        payment_id = payment.get("id")
        notes = payment.get("notes", {})
        user_id = notes.get("user_id")
        plan = notes.get("plan")

        if user_id and plan:
            await execute("UPDATE users SET subscription_plan = $1 WHERE id = $2", plan, user_id)
            await execute(
                """INSERT INTO subscriptions (user_id, plan, razorpay_payment_id, status, started_at)
                   VALUES ($1, $2, $3, 'active', NOW())""",
                user_id, plan, payment_id
            )

    return {"status": "ok"}
