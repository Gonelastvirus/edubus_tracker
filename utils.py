import math
from typing import List, Tuple
from datetime import datetime
from database import Station, BusLocation
from config import AVERAGE_BUS_SPEED_KMH, APPROACHING_DISTANCE_KM

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def calculate_eta_minutes(distance_km: float, speed_kmh: float = AVERAGE_BUS_SPEED_KMH) -> int:
    """Calculate estimated time of arrival in minutes"""
    if distance_km <= 0:
        return 0
    hours = distance_km / speed_kmh
    minutes = hours * 60
    return int(round(minutes))

def determine_station_status(bus_location: BusLocation, station: Station, stations: List[Station]) -> Tuple[str, int]:
    """
    Determine station status and ETA
    Returns tuple of (status, eta_minutes)
    """
    if not bus_location:
        return "waiting", None
    
    distance = haversine_distance(
        bus_location.latitude, bus_location.longitude,
        station.latitude, station.longitude
    )
    
    # Check if bus has passed this station by comparing with other stations
    current_station = find_closest_station_to_bus(bus_location, stations)
    if current_station and current_station.order_number > station.order_number:
        return "passed", 0
    
    # Check if bus is approaching (within 1km)
    if distance <= APPROACHING_DISTANCE_KM:
        eta = calculate_eta_minutes(distance)
        return "approaching", eta
    
    # Calculate route distance considering station order
    route_distance = calculate_route_distance(bus_location, station, stations)
    eta = calculate_eta_minutes(route_distance)
    return "waiting", eta

def find_closest_station_to_bus(bus_location: BusLocation, stations: List[Station]) -> Station:
    """Find the station closest to the current bus location"""
    if not stations:
        return None
    
    closest_station = stations[0]
    min_distance = haversine_distance(
        bus_location.latitude, bus_location.longitude,
        closest_station.latitude, closest_station.longitude
    )
    
    for station in stations[1:]:
        distance = haversine_distance(
            bus_location.latitude, bus_location.longitude,
            station.latitude, station.longitude
        )
        if distance < min_distance:
            min_distance = distance
            closest_station = station
    
    return closest_station

def calculate_route_distance(bus_location: BusLocation, target_station: Station, stations: List[Station]) -> float:
    """
    Calculate approximate route distance considering station order
    This is a simplified calculation - in production you'd use actual route data
    """
    # Sort stations by order number
    sorted_stations = sorted(stations, key=lambda x: x.order_number)
    
    # Find current position in route
    closest_station = find_closest_station_to_bus(bus_location, sorted_stations)
    if not closest_station:
        return haversine_distance(
            bus_location.latitude, bus_location.longitude,
            target_station.latitude, target_station.longitude
        )
    
    # If target station is before current position, it's already passed
    if target_station.order_number <= closest_station.order_number:
        return 0
    
    # Calculate cumulative distance through route
    total_distance = haversine_distance(
        bus_location.latitude, bus_location.longitude,
        closest_station.latitude, closest_station.longitude
    )
    
    current_idx = next((i for i, s in enumerate(sorted_stations) if s.id == closest_station.id), 0)
    target_idx = next((i for i, s in enumerate(sorted_stations) if s.id == target_station.id), len(sorted_stations))
    
    # Add distances between consecutive stations
    for i in range(current_idx, min(target_idx, len(sorted_stations) - 1)):
        total_distance += haversine_distance(
            sorted_stations[i].latitude, sorted_stations[i].longitude,
            sorted_stations[i + 1].latitude, sorted_stations[i + 1].longitude
        )
    
    return total_distance