from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_type: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
    user_type: str  # "student" or "admin"

# Student Models
class StudentBase(BaseModel):
    name: str
    username: str
    assigned_bus_id: Optional[int] = None
    assigned_station_id: Optional[int] = None

class StudentCreate(StudentBase):
    password: str

class StudentResponse(StudentBase):
    id: int
    
    class Config:
        from_attributes = True

# Bus Models
class BusBase(BaseModel):
    bus_number: str
    driver_name: str
    driver_phone: str

class BusCreate(BusBase):
    pass

class BusResponse(BusBase):
    id: int
    
    class Config:
        from_attributes = True

# Station Models
class StationBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    bus_id: int
    order_number: int

class StationCreate(StationBase):
    pass

class StationUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    order_number: Optional[int] = None

class StationWithStatus(StationBase):
    id: int
    status: str  # "passed", "approaching", "waiting"
    eta_minutes: Optional[int] = None
    
    class Config:
        from_attributes = True

class StationResponse(StationBase):
    id: int
    
    class Config:
        from_attributes = True

# Bus Location Models
class BusLocationCreate(BaseModel):
    bus_id: int
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None

class BusLocationResponse(BaseModel):
    id: int
    bus_id: int
    latitude: float
    longitude: float
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Admin Models
class AdminCreate(BaseModel):
    username: str
    password: str