from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine
from app.api.routes import auth, partners, users, parcels, dashboard

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for Realmile Logistics Last-Mile Management System"
)

# Set up CORS (Cross-Origin Resource Sharing)
# This allows our frontend to talk to our backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Realmile Logistics API",
        "status": "Running",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health():
    """
    Liveness + readiness check used by Docker / load balancers.
    Returns 200 only if the API can reach the database, 503 otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "database": "unreachable"})
    return {"status": "ok", "database": "ok"}

app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["Authentication"])
app.include_router(partners.router, prefix=settings.API_V1_STR + "/partners", tags=["Partners"])
app.include_router(parcels.router, prefix=settings.API_V1_STR + "/parcels", tags=["Parcels"])
app.include_router(dashboard.router, prefix=settings.API_V1_STR + "/dashboard", tags=["Dashboard"])
app.include_router(users.router, prefix=settings.API_V1_STR + "/users", tags=["Users"])