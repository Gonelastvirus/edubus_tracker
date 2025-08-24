from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    assigned_bus_id = Column(Integer, ForeignKey("buses.id"), nullable=True)
    assigned_station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)
    
    bus = relationship("Bus", back_populates="students")
    station = relationship("Station", back_populates="students")

class Bus(Base):
    __tablename__ = "buses"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String, unique=True, nullable=False)
    driver_name = Column(String, nullable=False)
    driver_phone = Column(String, nullable=False)
    
    students = relationship("Student", back_populates="bus")
    stations = relationship("Station", back_populates="bus")
    locations = relationship("BusLocation", back_populates="bus")

class Station(Base):
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    order_number = Column(Integer, nullable=False)
    
    bus = relationship("Bus", back_populates="stations")
    students = relationship("Student", back_populates="station")

class BusLocation(Base):
    __tablename__ = "bus_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    bus = relationship("Bus", back_populates="locations")

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=True)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine)