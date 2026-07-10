import random
import datetime
from sqlalchemy.orm import Session
from app.models.models import Asset, SensorTelemetry

# Core sensor profiles per asset type
METRIC_PROFILES = {
    "Bridge": {
        "vibration": (0.05, 0.45, "mm/s"),
        "load": (12.0, 75.0, "tons"),
        "strain": (100.0, 450.0, "microstrain"),
        "wind_speed": (5.0, 45.0, "km/h")
    },
    "Dam": {
        "water_level": (185.0, 202.0, "meters"),
        "water_pressure": (2500.0, 3200.0, "kPa"),
        "vibration": (0.01, 0.15, "mm/s"),
        "seepage_rate": (2.0, 8.5, "L/s")
    },
    "PowerGrid": {
        "voltage": (485.0, 515.0, "kV"),
        "current": (200.0, 850.0, "A"),
        "temperature": (45.0, 95.0, "C"),
        "frequency": (59.8, 60.2, "Hz")
    },
    "Pipeline": {
        "pressure": (700.0, 1150.0, "psi"),
        "flow_rate": (120.0, 180.0, "L/s"),
        "temperature": (15.0, 32.0, "C"),
        "gas_leak_ppm": (0.0, 10.0, "ppm") # normally low
    },
    "Tunnel": {
        "carbon_monoxide": (2.0, 45.0, "ppm"),
        "vibration": (0.02, 0.35, "mm/s"),
        "traffic_count": (10.0, 250.0, "vehicles/min"),
        "humidity": (40.0, 85.0, "%")
    },
    "Railway": {
        "track_alignment_dev": (-2.0, 2.0, "mm"),
        "rail_temp": (15.0, 55.0, "C"),
        "passenger_load": (50.0, 1200.0, "people/hr"),
        "vibration": (0.05, 0.45, "mm/s")
    },
    "Airport": {
        "runway_deflection": (0.05, 1.2, "mm"),
        "pavement_temp": (10.0, 60.0, "C"),
        "wind_speed": (2.0, 40.0, "km/h")
    },
    "Ports": {
        "wind_speed": (5.0, 50.0, "km/h"),
        "wave_height": (0.1, 3.5, "meters"),
        "container_load": (50.0, 500.0, "tons")
    },
    "Telecommunication Towers": {
        "signal_attenuation": (0.5, 4.5, "dB"),
        "wind_speed": (5.0, 65.0, "km/h"),
        "battery_backup": (80.0, 100.0, "%"),
        "temperature": (15.0, 42.0, "C")
    }
}

def generate_live_telemetry_point(asset_type: str, metric_name: str, status: str = "Healthy") -> float:
    profile = METRIC_PROFILES.get(asset_type, {}).get(metric_name)
    if not profile:
        return random.uniform(10.0, 100.0)
    
    min_val, max_val, _ = profile
    
    # Introduce anomalies for Warning and Critical assets
    if status == "Warning":
        # Shift average higher or lower
        shift = (max_val - min_val) * 0.25
        if random.choice([True, False]):
            return random.uniform(max_val - shift, max_val + shift)
        else:
            return random.uniform(min_val - shift, min_val + shift)
    elif status == "Critical":
        # Return severe out-of-bounds measurements
        shift = (max_val - min_val) * 0.6
        if random.choice([True, False]):
            return random.uniform(max_val, max_val + shift)
        else:
            return random.uniform(min_val - shift, min_val)
            
    return random.uniform(min_val, max_val)

def stream_sensor_telemetry(db: Session) -> list[SensorTelemetry]:
    """
    Simulates a single time step of live sensor telemetry updates for all assets in the system.
    Saves the new points to the database.
    """
    assets = db.query(Asset).all()
    new_telemetries = []
    
    now = datetime.datetime.utcnow()
    for asset in assets:
        profile = METRIC_PROFILES.get(asset.type)
        if not profile:
            continue
        
        # Determine metrics to stream
        for metric_name in profile.keys():
            val = generate_live_telemetry_point(asset.type, metric_name, asset.status)
            telemetry = SensorTelemetry(
                asset_id=asset.id,
                metric_name=metric_name,
                value=val,
                timestamp=now
            )
            new_telemetries.append(telemetry)
            
    db.add_all(new_telemetries)
    db.commit()
    return new_telemetries

def get_latest_telemetry_dict(db: Session, asset_id: str) -> dict[str, float]:
    """
    Returns a dictionary of the latest sensor telemetry readings for an asset.
    """
    latest_points = {}
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return latest_points
        
    profile = METRIC_PROFILES.get(asset.type)
    if not profile:
        return latest_points
        
    for metric_name in profile.keys():
        last_t = db.query(SensorTelemetry)\
            .filter(SensorTelemetry.asset_id == asset_id, SensorTelemetry.metric_name == metric_name)\
            .order_by(SensorTelemetry.timestamp.desc())\
            .first()
        if last_t:
            latest_points[metric_name] = last_t.value
        else:
            # Generate default base value if none in DB
            latest_points[metric_name] = (profile[metric_name][0] + profile[metric_name][1]) / 2.0
            
    return latest_points
