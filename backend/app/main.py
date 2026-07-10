import time
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config.settings import settings
from app.config.database import engine, Base
from app.api import api_router
from app.websocket.connection_manager import router as ws_router
from app.ml.services import ml_manager

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("inframind_logger")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered National Critical Infrastructure Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request processing time measurement middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Custom Database Error Handler
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database anomaly detected: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database transaction failure. Please retry or contact administration."}
    )

# General Exception Handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"System runtime error: {str(exc)}"}
    )

# Mounting routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)

@app.on_event("startup")
def on_startup():
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Verifying ML models state...")
    # Trigger loading/building ML models on boot
    _ = ml_manager.classes
    
    logger.info(f"{settings.PROJECT_NAME} backend service successfully started.")

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "platform": settings.PROJECT_NAME,
        "api_docs": "/docs",
        "version": "1.0.0",
        "timestamp": time.time()
    }
