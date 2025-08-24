from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, Station, Bus, BusLocation
from models import StationWithStatus, BusResponse, BusLocationResponse
from auth import get_current_student
from utils import determine_station_status

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/stations/{bus_id}", response_model=List[StationWithStatus])
def get_stations_with_status(
    bus_id: int,
    db: Session = Depends(get_db),
    current_student = Depends(get_current_student)
):
    # Verify student has access to this bus
    if current_student.assigned_bus_id != bus_id:
        raise HTTPException(status_code=403, detail="Access denied to this bus")
    
    # Get all stations for the bus
    stations = db.query(Station).filter(Station.bus_id == bus_id).order_by(Station.order_number).all()
    if not stations:
        return []
    
    # Get latest bus location
    latest_location = db.query(BusLocation).filter(
        BusLocation.bus_id == bus_id
    ).order_by(BusLocation.timestamp.desc()).first()
    
    stations_with_status = []
    for station in stations:
        status, eta = determine_station_status(latest_location, station, stations)
        
        station_data = {
            "id": station.id,
            "name": station.name,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "bus_id": station.bus_id,
            "order_number": station.order_number,
            "status": status,
            "eta_minutes": eta
        }
        stations_with_status.append(StationWithStatus(**station_data))
    
    return stations_with_status

@router.get("/bus/{bus_id}", response_model=BusResponse)
def get_bus_info(
    bus_id: int,
    db: Session = Depends(get_db),
    current_student = Depends(get_current_student)
):
    # Verify student has access to this bus
    if current_student.assigned_bus_id != bus_id:
        raise HTTPException(status_code=403, detail="Access denied to this bus")
    
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    return bus

@router.get("/bus/{bus_id}/location", response_model=Optional[BusLocationResponse])
def get_bus_location(
    bus_id: int,
    db: Session = Depends(get_db),
    current_student = Depends(get_current_student)
):
    # Verify student has access to this bus
    if current_student.assigned_bus_id != bus_id:
        raise HTTPException(status_code=403, detail="Access denied to this bus")
    
    latest_location = db.query(BusLocation).filter(
        BusLocation.bus_id == bus_id
    ).order_by(BusLocation.timestamp.desc()).first()
    
    if not latest_location:
        return None
    
    return latest_location

@router.get("/my-bus", response_model=Optional[BusResponse])
def get_my_bus(
    db: Session = Depends(get_db),
    current_student = Depends(get_current_student)
):
    if not current_student.assigned_bus_id:
        return None
    
    bus = db.query(Bus).filter(Bus.id == current_student.assigned_bus_id).first()
    return bus

@router.get("/my-station", response_model=Optional[StationWithStatus])
def get_my_station_status(
    db: Session = Depends(get_db),
    current_student = Depends(get_current_student)
):
    if not current_student.assigned_station_id or not current_student.assigned_bus_id:
        return None
    
    station = db.query(Station).filter(Station.id == current_student.assigned_station_id).first()
    if not station:
        return None
    
    # Get all stations for route calculation
    all_stations = db.query(Station).filter(
        Station.bus_id == current_student.assigned_bus_id
    ).order_by(Station.order_number).all()
    
    # Get latest bus location
    latest_location = db.query(BusLocation).filter(
        BusLocation.bus_id == current_student.assigned_bus_id
    ).order_by(BusLocation.timestamp.desc()).first()
    
    status, eta = determine_station_status(latest_location, station, all_stations)
    
    return StationWithStatus(
        id=station.id,
        name=station.name,
        latitude=station.latitude,
        longitude=station.longitude,
        bus_id=station.bus_id,
        order_number=station.order_number,
        status=status,
        eta_minutes=eta
    )