# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.db import Base, engine
from app.models import user, parking_analytics, spot_status, vehicle, parking_lot, parking_spot
from app.api import lot_routes, auth_routes
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        pass

app = FastAPI(title="ParkVision API", lifespan=lifespan)

origins = [
    "http://localhost:8081",  # your frontend URL
    # add more if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],       # allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],       # allow all headers
)

app.include_router(lot_routes.router)
app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"message": "Hello, World!"}