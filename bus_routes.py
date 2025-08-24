from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, BusLocation, Bus
from models import BusLocationCreate, BusLocationResponse

router = APIRouter(prefix="/bus", tags=["bus-hardware"])

@router.post("/update", response_model=BusLocationResponse)
def update_bus_location(
    location_data: BusLocationCreate,
    db: Session = Depends(get_db)
):
    # Verify bus exists
    bus = db.query(Bus).filter(Bus.id == location_data.bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Use provided timestamp or current time
    timestamp = location_data.timestamp or datetime.utcnow()
    
    # Create new location record
    db_location = BusLocation(
        bus_id=location_data.bus_id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        timestamp=timestamp
    )
    
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    
    return db_location

@router.get("/locations/{bus_id}", response_model=list[BusLocationResponse])
def get_bus_location_history(
    bus_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    # Verify bus exists
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    locations = db.query(BusLocation).filter(
        BusLocation.bus_id == bus_id
    ).order_by(BusLocation.timestamp.desc()).limit(limit).all()
    
    return locations

@router.get("/health")
def bus_api_health():
    """Health check endpoint for bus hardware"""
    return {"status": "ok", "message": "Bus API is running"}