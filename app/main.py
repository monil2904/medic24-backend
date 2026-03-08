from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db_pool, close_db_pool
from app.routes import auth, chat, image, lab_report, webhook
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    await init_db_pool()
    yield
    # on shutdown
    await close_db_pool()

app = FastAPI(title="Med24 AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://med24ai.in",
        "https://www.med24ai.in",
        "https://medic24.vercel.app",       # update with your actual Vercel URL after first deploy
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(chat.router, prefix="/api/v1/chat")
app.include_router(image.router, prefix="/api/v1/chat/image")
app.include_router(lab_report.router, prefix="/api/v1/lab-report")
app.include_router(webhook.router, prefix="/api/v1/razorpay")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
