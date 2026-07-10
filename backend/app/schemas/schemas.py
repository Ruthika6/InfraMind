from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- AUTH SCHEMAS ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "operator"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# --- ASSET SCHEMAS ---
class AssetBase(BaseModel):
    id: str
    name: str
    type: str
    location: str
    owner: str
    construction_material: Optional[str] = None
    age_years: int = 0
    gis_latitude: float
    gis_longitude: float
    structural_specs: Optional[Dict[str, Any]] = None

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    health_score: float
    rul_months: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- TELEMETRY SCHEMAS ---
class SensorTelemetryBase(BaseModel):
    asset_id: str
    metric_name: str
    value: float

class SensorTelemetryResponse(SensorTelemetryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class LiveTelemetryResponse(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: str
    timestamp: datetime
    telemetry: Dict[str, float]
    status: str
    health_score: float


# --- ML & PREDICTION SCHEMAS ---
class PredictRequest(BaseModel):
    asset_id: str

class PredictResponse(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: str
    risk_score: float  # 0 to 100
    confidence: float  # 0 to 1
    remaining_life_months: float
    anomaly_detected: bool
    failure_classification: str  # e.g., "Structural Crack", "No Failure", "Transformer Insulation Breakdown"
    recommended_inspection_date: datetime
    recommended_repair_priority: str  # Low, Medium, High, Critical


# --- EXPLAINABILITY SCHEMAS ---
class SHAPFeatureImportance(BaseModel):
    feature_name: str
    importance_value: float
    impact_direction: str  # Positive, Negative, Neutral

class ExplainResponse(BaseModel):
    asset_id: str
    prediction: PredictResponse
    shap_values: List[SHAPFeatureImportance]
    explanation_text: str
    alternative_scenarios: Dict[str, str]
    timestamp: datetime


# --- FORECAST SCHEMAS ---
class ForecastRequest(BaseModel):
    asset_id: str
    metric_name: str
    horizon_days: int = 30

class ForecastDataPoint(BaseModel):
    timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float

class ForecastResponse(BaseModel):
    asset_id: str
    metric_name: str
    forecast: List[ForecastDataPoint]
    historical_avg: float
    predicted_trend: str  # Increasing, Decreasing, Stable


# --- EMERGENCY RESPONSE SCHEMAS ---
class EmergencyResource(BaseModel):
    type: str  # Ambulance, Fire Truck, Police Patrol, Evacuation Bus
    units: int
    eta_minutes: float
    status: str

class ShelterAllocation(BaseModel):
    shelter_name: str
    gis_latitude: float
    gis_longitude: float
    capacity_allocated: int
    distance_km: float

class EmergencyResponsePlan(BaseModel):
    id: str
    asset_id: str
    severity: str  # Moderate, Severe, Extreme
    incident_type: str  # Dam Overflow, Bridge Stress Fracture, Power Substation Fire
    evacuation_required: bool
    evacuation_radius_km: float
    evacuation_routes: List[List[float]]  # list of GIS coordinate paths
    dispatch_resources: List[EmergencyResource]
    shelter_allocation: List[ShelterAllocation]
    drone_mission_id: Optional[str] = None
    approval_status: str  # Pending, Approved, Rejected
    created_at: datetime


# --- DISASTER SIMULATION SCHEMAS ---
class SimulationRequest(BaseModel):
    disaster_type: str  # Earthquake, Cyclone, Dam Breach, Chemical Leak, Power Outage, Wildfire
    gis_latitude: float
    gis_longitude: float
    radius_km: float
    intensity: float  # Richter scale for Earthquake (e.g. 5.0 - 9.0), Category for Cyclone (1 - 5)

class SimulationResponse(BaseModel):
    disaster_type: str
    gis_latitude: float
    gis_longitude: float
    radius_km: float
    intensity: float
    economic_loss_millions: float
    population_impacted: int
    affected_assets: List[AssetResponse]
    repair_cost_millions: float
    response_timeline_days: float
    evacuation_recommended: bool
    summary_report: str


# --- DRONE METRIC SCHEMAS ---
class DroneMissionResponse(BaseModel):
    id: str
    name: str
    battery_pct: float
    altitude_m: float
    speed_kmh: float
    latitude: float
    longitude: float
    camera_status: str
    mission_status: str
    current_mission_details: Optional[str] = None
    detection_metadata: Optional[Dict[str, Any]] = None
    last_updated: datetime

    class Config:
        from_attributes = True


# --- CITIZEN SCHEMAS ---
class CitizenReportCreate(BaseModel):
    reporter_name: Optional[str] = "Anonymous"
    contact_info: Optional[str] = None
    report_type: str
    description: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None

class CitizenReportResponse(CitizenReportCreate):
    id: int
    status: str
    gemini_summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- EXECUTIVE DASHBOARD SCHEMAS ---
class CityRanking(BaseModel):
    city_name: str
    health_score: float
    alert_count: int

class DashboardSummary(BaseModel):
    national_health_score: float
    active_alerts_count: int
    critical_risk_assets_count: int
    maintenance_backlog_count: int
    city_rankings: List[CityRanking]
    budget_utilization_pct: float
    carbon_impact_saved_tons: float
    top_risks: List[Dict[str, Any]]
    sensor_stream_rate_hz: float
