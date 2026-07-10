import uuid
import datetime
from sqlalchemy.orm import Session
from app.models.models import Asset, DroneMission
from app.schemas.schemas import EmergencyResponsePlan, EmergencyResource, ShelterAllocation

def generate_emergency_plan(db: Session, asset_id: str) -> EmergencyResponsePlan:
    # 1. Fetch asset details
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise ValueError(f"Asset with ID {asset_id} not found.")
        
    # 2. Determine severity based on health score
    health = asset.health_score
    if health < 50.0:
        severity = "Extreme"
        evac_required = True
        radius = 5.0
    elif health < 75.0:
        severity = "Severe"
        evac_required = True
        radius = 2.0
    else:
        severity = "Moderate"
        evac_required = False
        radius = 0.0
        
    # 3. Create evacuation routes (GPS coordinate paths) radiating outward
    routes = []
    if evac_required:
        # Create 3 directional routing paths: North, East, Southwest
        lat, lon = asset.gis_latitude, asset.gis_longitude
        routes = [
            [[lat, lon], [lat + 0.015, lon], [lat + 0.030, lon + 0.005]], # Route Alpha (North)
            [[lat, lon], [lat, lon - 0.015], [lat - 0.010, lon - 0.030]], # Route Beta (West/South)
        ]
        
    # 4. Allocate emergency vehicles & assets
    resources = []
    if severity == "Extreme":
        resources = [
            EmergencyResource(type="Evacuation Bus", units=12, eta_minutes=15.0, status="Dispatched"),
            EmergencyResource(type="Ambulance", units=6, eta_minutes=8.0, status="Dispatched"),
            EmergencyResource(type="Fire Engine", units=4, eta_minutes=10.0, status="En Route"),
            EmergencyResource(type="Police Patrol", units=8, eta_minutes=5.0, status="On Scene")
        ]
    elif severity == "Severe":
        resources = [
            EmergencyResource(type="Evacuation Bus", units=4, eta_minutes=20.0, status="Standby"),
            EmergencyResource(type="Ambulance", units=2, eta_minutes=12.0, status="Dispatched"),
            EmergencyResource(type="Fire Engine", units=1, eta_minutes=15.0, status="En Route"),
            EmergencyResource(type="Police Patrol", units=3, eta_minutes=7.0, status="On Scene")
        ]
    else:
        resources = [
            EmergencyResource(type="Ambulance", units=1, eta_minutes=15.0, status="Standby"),
            EmergencyResource(type="Police Patrol", units=1, eta_minutes=10.0, status="On Scene")
        ]
        
    # 5. Allocate shelters
    shelters = [
        ShelterAllocation(
            shelter_name="Aegis Civic Arena",
            gis_latitude=asset.gis_latitude + 0.025,
            gis_longitude=asset.gis_longitude + 0.015,
            capacity_allocated=1500 if severity == "Extreme" else 400,
            distance_km=3.2
        ),
        ShelterAllocation(
            shelter_name="Sector 4 Community Shelter",
            gis_latitude=asset.gis_latitude - 0.020,
            gis_longitude=asset.gis_longitude - 0.025,
            capacity_allocated=800 if severity == "Extreme" else 200,
            distance_km=4.1
        )
    ]
    
    # 6. Check for active drone dispatch or configure a mission
    drone_mission = db.query(DroneMission).filter(DroneMission.mission_status == "Idle").first()
    drone_id = None
    if drone_mission:
        # Mutate drone state to dispatch it to help emergency coordinates
        drone_mission.mission_status = "Emergency Dispatch"
        drone_mission.latitude = asset.gis_latitude + 0.002
        drone_mission.longitude = asset.gis_longitude + 0.002
        drone_mission.current_mission_details = f"Emergency hazard mapping active for asset: {asset.name}."
        db.commit()
        drone_id = drone_mission.id
        
    # 7. Map details
    incident_type_map = {
        "Bridge": "Bridge Structural Fracture",
        "Dam": "Dam Reservoir Overflow Breach Risk",
        "PowerGrid": "Substation Power Transformer Explosion",
        "Pipeline": "Pressurized Gas Pipeline Corrosion Leakage",
        "Tunnel": "Tunnel Carbon Monoxide Inundation",
        "Railway": "Transit Track Misalignment Failure",
        "Airport": "Runway Asphalt Deflection Fracture",
        "Ports": "Deepwater Wharf Pile Structural Defect",
        "Telecommunication Towers": "Telecom Tower Wind Shear Deflection"
    }
    incident_type = incident_type_map.get(asset.type, "Infrastructure Failure Risk")
    
    return EmergencyResponsePlan(
        id=f"plan_{uuid.uuid4().hex[:8]}",
        asset_id=asset_id,
        severity=severity,
        incident_type=incident_type,
        evacuation_required=evac_required,
        evacuation_radius_km=radius,
        evacuation_routes=routes,
        dispatch_resources=resources,
        shelter_allocation=shelters,
        drone_mission_id=drone_id,
        approval_status="Pending", # Requires human verification
        created_at=datetime.datetime.utcnow()
    )
