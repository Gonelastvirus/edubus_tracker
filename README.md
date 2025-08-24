# School Bus Tracking API

A comprehensive FastAPI backend for school bus tracking system with real-time GPS updates, JWT authentication, and Flutter-ready CORS configuration.

## Features

- **Authentication**: JWT-based authentication for students and admin
- **Real-time GPS Tracking**: Receive and process GPS updates from Arduino hardware
- **ETA Calculation**: Haversine formula for accurate distance and time estimates
- **Station Status**: Automatic status updates (passed/approaching/waiting)
- **Admin Management**: Complete CRUD operations for buses, stations, and students
- **Student APIs**: View bus status, station information, and ETA

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run the server**:
   ```bash
   python main.py
   ```

4. **Access the API**:
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

## Initial Setup

1. **Create an admin account**:
   ```bash
   curl -X POST "http://localhost:8000/admin/create-admin" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "adminpassword"}'
   ```

2. **Login to get JWT token**:
   ```bash
   curl -X POST "http://localhost:8000/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "adminpassword", "user_type": "admin"}'
   ```

## API Endpoints

### Authentication
- `POST /login` - Login for students and admin

### Admin APIs
- `POST /admin/stations` - Create station
- `GET /admin/stations/{bus_id}` - List stations for bus
- `PUT /admin/stations/{id}` - Update station
- `DELETE /admin/stations/{id}` - Delete station
- `POST /admin/students` - Create student
- `POST /admin/buses` - Create bus

### Student APIs
- `GET /student/stations/{bus_id}` - Get stations with status and ETA
- `GET /student/bus/{bus_id}` - Get bus information
- `GET /student/bus/{bus_id}/location` - Get latest bus location
- `GET /student/my-bus` - Get assigned bus info
- `GET /student/my-station` - Get assigned station status

### Bus Hardware APIs
- `POST /bus/update` - Update GPS location from Arduino
- `GET /bus/locations/{bus_id}` - Get location history

## Arduino Integration

Send GPS updates to `/bus/update` endpoint:

```json
{
  "bus_id": 1,
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timestamp": "2025-01-09T10:30:00Z"
}
```

## Database Models

- **Students**: Authentication and bus assignment
- **Buses**: Bus information and driver details
- **Stations**: Route stations with coordinates and order
- **BusLocations**: Real-time GPS tracking data
- **Admins**: Admin user authentication

## Business Logic

- **ETA Calculation**: Uses Haversine formula for accurate distance
- **Station Status**:
  - `passed`: Bus has crossed station coordinates
  - `approaching`: Bus within 1km of station
  - `waiting`: Bus not yet approaching
- **Route Distance**: Considers station order for accurate ETA

## Security

- JWT tokens for authentication
- Password hashing with bcrypt
- Role-based access control
- CORS configuration for Flutter frontend

## Configuration

Key settings in `config.py`:
- `AVERAGE_BUS_SPEED_KMH`: Default bus speed for ETA calculation
- `APPROACHING_DISTANCE_KM`: Distance threshold for "approaching" status
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time