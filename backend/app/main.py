# backend/app/main.py
from fastapi import FastAPI
from app.utils.db import Base, engine
from app.models import user, parking_analytics, spot_status, vehicle, parking_lot, parking_spot
from app.api import lot_routes

Base.metadata.create_all(bind=engine)
app = FastAPI(title="ParkVision API")
app.include_router(lot_routes.router)

@app.get("/")
def root():
    return {"message": "Hello, World!"}