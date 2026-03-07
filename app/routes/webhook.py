from fastapi import APIRouter

router = APIRouter()

@router.post("/webhook")
async def razorpay_webhook():
    pass
