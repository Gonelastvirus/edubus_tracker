from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db, Student, Bus, Station, BusLocation, Admin
from models import LoginRequest, Token
from auth import authenticate_user, create_access_token, get_password_hash
from config import ACCESS_TOKEN_EXPIRE_MINUTES
import admin_routes
import student_routes
import bus_routes
import os

app = FastAPI(
    title="School Bus Tracking API",
    description="Backend API for school bus tracking system with real-time GPS updates",
    version="1.0.0"
)

# CORS middleware for Flutter frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_routes.router)
app.include_router(student_routes.router)
app.include_router(bus_routes.router)

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {
        "message": "School Bus Tracking API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Web GUI Routes
@app.get("/gui", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/gui/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    buses = db.query(Bus).all()
    students = db.query(Student).all()
    stations = db.query(Station).all()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "buses": buses,
        "students": students,
        "stations": stations
    })

@app.get("/gui/student", response_class=HTMLResponse)
async def student_dashboard(request: Request, db: Session = Depends(get_db)):
    buses = db.query(Bus).all()
    return templates.TemplateResponse("student.html", {
        "request": request,
        "buses": buses
    })

@app.get("/gui/api-docs", response_class=HTMLResponse)
async def api_documentation(request: Request):
    return templates.TemplateResponse("api_docs.html", {"request": request})

@app.get("/gui/bus-simulator", response_class=HTMLResponse)
async def bus_simulator(request: Request, db: Session = Depends(get_db)):
    buses = db.query(Bus).all()
    return templates.TemplateResponse("bus_simulator.html", {
        "request": request,
        "buses": buses
    })

# Admin form handlers
@app.post("/gui/admin/create-bus")
async def create_bus_form(
    request: Request,
    bus_number: str = Form(...),
    driver_name: str = Form(...),
    driver_phone: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if bus number already exists
    if db.query(Bus).filter(Bus.bus_number == bus_number).first():
        return RedirectResponse(url="/gui/admin?error=Bus number already exists", status_code=303)
    
    db_bus = Bus(
        bus_number=bus_number,
        driver_name=driver_name,
        driver_phone=driver_phone
    )
    db.add(db_bus)
    db.commit()
    return RedirectResponse(url="/gui/admin?success=Bus created successfully", status_code=303)

@app.post("/gui/admin/create-station")
async def create_station_form(
    request: Request,
    name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    bus_id: int = Form(...),
    order_number: int = Form(...),
    db: Session = Depends(get_db)
):
    db_station = Station(
        name=name,
        latitude=latitude,
        longitude=longitude,
        bus_id=bus_id,
        order_number=order_number
    )
    db.add(db_station)
    db.commit()
    return RedirectResponse(url="/gui/admin?success=Station created successfully", status_code=303)

@app.post("/gui/admin/create-student")
async def create_student_form(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    assigned_bus_id: int = Form(None),
    assigned_station_id: int = Form(None),
    db: Session = Depends(get_db)
):
    # Check if username already exists
    if db.query(Student).filter(Student.username == username).first():
        return RedirectResponse(url="/gui/admin?error=Username already exists", status_code=303)
    
    hashed_password = get_password_hash(password)
    db_student = Student(
        name=name,
        username=username,
        password_hash=hashed_password,
        assigned_bus_id=assigned_bus_id if assigned_bus_id else None,
        assigned_station_id=assigned_station_id if assigned_station_id else None
    )
    db.add(db_student)
    db.commit()
    return RedirectResponse(url="/gui/admin?success=Student created successfully", status_code=303)

@app.post("/gui/admin/create-admin")
async def create_admin_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if admin already exists
    existing_admin = db.query(Admin).first()
    if existing_admin:
        return RedirectResponse(url="/gui/admin?error=Admin already exists", status_code=303)
    
    hashed_password = get_password_hash(password)
    db_admin = Admin(
        username=username,
        password_hash=hashed_password,
        is_admin=True
    )
    db.add(db_admin)
    db.commit()
    return RedirectResponse(url="/gui/admin?success=Admin created successfully", status_code=303)

# Bus simulator form handler
@app.post("/gui/bus-simulator/update")
async def update_bus_location_form(
    request: Request,
    bus_id: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    
    db_location = BusLocation(
        bus_id=bus_id,
        latitude=latitude,
        longitude=longitude,
        timestamp=datetime.utcnow()
    )
    db.add(db_location)
    db.commit()
    return RedirectResponse(url="/gui/bus-simulator?success=Location updated successfully", status_code=303)

# API Routes
@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.username, login_data.password, login_data.user_type)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_type": login_data.user_type},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": login_data.user_type
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "School Bus Tracking API is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)