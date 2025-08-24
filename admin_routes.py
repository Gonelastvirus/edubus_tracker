from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Station, Student, Bus, Admin
from models import (
    StationCreate, StationResponse, StationUpdate,
    StudentCreate, StudentResponse,
    BusCreate, BusResponse,
    AdminCreate
)
from auth import get_current_admin, get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])

# Station management
@router.post("/stations", response_model=StationResponse)
def create_station(
    station: StationCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # Verify bus exists
    bus = db.query(Bus).filter(Bus.id == station.bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    db_station = Station(**station.dict())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

@router.get("/stations/{bus_id}", response_model=List[StationResponse])
def list_stations(
    bus_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    stations = db.query(Station).filter(Station.bus_id == bus_id).order_by(Station.order_number).all()
    return stations

@router.put("/stations/{station_id}", response_model=StationResponse)
def update_station(
    station_id: int,
    station_update: StationUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    db_station = db.query(Station).filter(Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    update_data = station_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_station, key, value)
    
    db.commit()
    db.refresh(db_station)
    return db_station

@router.delete("/stations/{station_id}")
def delete_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    db_station = db.query(Station).filter(Station.id == station_id).first()
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    db.delete(db_station)
    db.commit()
    return {"message": "Station deleted successfully"}

# Student management
@router.post("/students", response_model=StudentResponse)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # Check if username already exists
    if db.query(Student).filter(Student.username == student.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Verify bus exists if assigned
    if student.assigned_bus_id:
        bus = db.query(Bus).filter(Bus.id == student.assigned_bus_id).first()
        if not bus:
            raise HTTPException(status_code=404, detail="Bus not found")
    
    # Verify station exists if assigned
    if student.assigned_station_id:
        station = db.query(Station).filter(Station.id == student.assigned_station_id).first()
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
    
    hashed_password = get_password_hash(student.password)
    db_student = Student(
        name=student.name,
        username=student.username,
        password_hash=hashed_password,
        assigned_bus_id=student.assigned_bus_id,
        assigned_station_id=student.assigned_station_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/students", response_model=List[StudentResponse])
def list_students(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    students = db.query(Student).all()
    return students

# Bus management
@router.post("/buses", response_model=BusResponse)
def create_bus(
    bus: BusCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # Check if bus number already exists
    if db.query(Bus).filter(Bus.bus_number == bus.bus_number).first():
        raise HTTPException(status_code=400, detail="Bus number already exists")
    
    db_bus = Bus(**bus.dict())
    db.add(db_bus)
    db.commit()
    db.refresh(db_bus)
    return db_bus

@router.get("/buses", response_model=List[BusResponse])
def list_buses(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    buses = db.query(Bus).all()
    return buses

# Admin creation (for initial setup)
@router.post("/create-admin")
def create_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db)
):
    # Check if any admin exists (only allow if no admins exist)
    existing_admin = db.query(Admin).first()
    if existing_admin:
        raise HTTPException(status_code=403, detail="Admin already exists")
    
    hashed_password = get_password_hash(admin.password)
    db_admin = Admin(
        username=admin.username,
        password_hash=hashed_password,
        is_admin=True
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return {"message": "Admin created successfully"}