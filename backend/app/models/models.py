from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="operator")  # admin, operator, government, citizen
    full_name = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(100), index=True, nullable=False)  # Bridge, Dam, Railway, PowerGrid, Pipeline, etc.
    location = Column(String(255), nullable=False)
    owner = Column(String(150), nullable=False)
    construction_material = Column(String(150), nullable=True)
    age_years = Column(Integer, default=0)
    
    # Coordinates
    gis_latitude = Column(Float, nullable=False)
    gis_longitude = Column(Float, nullable=False)
    
    # Real-time Indicators (summarized or predictive)
    health_score = Column(Float, default=100.0)  # 0 to 100
    rul_months = Column(Float, default=240.0)    # Remaining Useful Life
    status = Column(String(50), default="Healthy")  # Healthy, Warning, Critical, Under Maintenance
    
    # Extended structural metadata
    structural_specs = Column(JSON, nullable=True)  # custom fields e.g., bridge span, pipe diameter, dam capacity
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    telemetry = relationship("SensorTelemetry", back_populates="asset", cascade="all, delete-orphan")
    maintenance_logs = relationship("MaintenanceLog", back_populates="asset", cascade="all, delete-orphan")

class SensorTelemetry(Base):
    __tablename__ = "sensor_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(100), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_name = Column(String(100), index=True, nullable=False)  # temperature, vibration, voltage, water_level
    value = Column(Float, nullable=False)

    asset = relationship("Asset", back_populates="telemetry")

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(100), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    cost = Column(Float, default=0.0)
    action_taken = Column(String(255), nullable=True)
    maintenance_date = Column(DateTime, default=datetime.utcnow)
    priority = Column(String(50), default="Medium")  # Low, Medium, High, Emergency
    status = Column(String(50), default="Scheduled") # Scheduled, In Progress, Completed, Cancelled

    asset = relationship("Asset", back_populates="maintenance_logs")

class DroneMission(Base):
    __tablename__ = "drone_missions"

    id = Column(String(100), primary_key=True, index=True)  # drone ID
    name = Column(String(100), nullable=False)
    battery_pct = Column(Float, default=100.0)
    altitude_m = Column(Float, default=0.0)
    speed_kmh = Column(Float, default=0.0)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    camera_status = Column(String(50), default="Active")  # Active, Offline, Recording
    mission_status = Column(String(50), default="Idle")  # Idle, Patrolling, En Route, Emergency Dispatch
    current_mission_details = Column(String(255), nullable=True)
    detection_metadata = Column(JSON, nullable=True)  # object detection e.g., {"cracks_detected": 2, "vegetation_overgrowth": false}
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_name = Column(String(150), default="Anonymous")
    contact_info = Column(String(150), nullable=True)
    report_type = Column(String(100), index=True, nullable=False)  # Pothole, Flooding, Gas Leak, Tree, Bridge Photo
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(255), nullable=True)
    status = Column(String(50), default="Submitted")  # Submitted, Investigating, Resolved, Rejected
    gemini_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentInteraction(Base):
    __tablename__ = "agent_interactions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(100), index=True, nullable=False)
    sender = Column(String(100), nullable=False)
    recipient = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    agent_state = Column(JSON, nullable=True)  # store system states or context values
    timestamp = Column(DateTime, default=datetime.utcnow)

class DisasterSimulation(Base):
    __tablename__ = "disaster_simulations"

    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String(100), nullable=False)  # Earthquake, Cyclone, Dam Breach, Chemical Leak, etc.
    severity = Column(Float, default=1.0)  # 0 to 1
    economic_loss_millions = Column(Float, default=0.0)
    population_impacted = Column(Integer, default=0)
    affected_assets_ids = Column(JSON, nullable=True)  # list of affected asset IDs
    response_days = Column(Float, default=1.0)
    repair_cost_millions = Column(Float, default=0.0)
    simulation_time = Column(DateTime, default=datetime.utcnow)
