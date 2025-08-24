import os
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./school_bus.db")

# Bus Configuration
AVERAGE_BUS_SPEED_KMH = 30  # Average bus speed in km/h
APPROACHING_DISTANCE_KM = 1.0  # Distance in km to consider bus "approaching"