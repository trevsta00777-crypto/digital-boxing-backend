from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.config import settings
from app.middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from app.routes.events import router as events_router
from app.routes.fighters import router as fighters_router
from app.routes.matches import router as matches_router
from app.routes.payments import router as payments_router
from app.routes.training import router as training_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Boxing Management Backend API",
    version="2.1.0",
)

origins = settings.cors_origins_list
if not origins and not settings.is_production:
    origins = ["http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Stripe-Signature"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth_router)
app.include_router(fighters_router)
app.include_router(events_router)
app.include_router(matches_router)
app.include_router(training_router)
app.include_router(payments_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.ENV, "version": "2.1.0"}


@app.get("/")
def root():
    return {
        "message": "Boxing Management API",
        "version": "2.1.0",
        "docs": "/docs",
    }
