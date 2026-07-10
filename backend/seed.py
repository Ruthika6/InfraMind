import random
import datetime
from sqlalchemy.orm import Session
from app.config.database import SessionLocal, Base, engine
from app.models.models import User, Asset, SensorTelemetry, MaintenanceLog, DroneMission, CitizenReport
from app.auth.auth_handler import get_password_hash

def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Seed Users
        if db.query(User).count() == 0:
            print("Seeding Users...")
            users = [
                User(
                    username="admin",
                    email="admin@inframind.gov",
                    hashed_password=get_password_hash("admin123"),
                    role="admin",
                    full_name="National Infrastructure Administrator"
                ),
                User(
                    username="operator1",
                    email="operator1@inframind.gov",
                    hashed_password=get_password_hash("operator123"),
                    role="operator",
                    full_name="Operations Center Lead"
                ),
                User(
                    username="citizen1",
                    email="citizen@outlook.com",
                    hashed_password=get_password_hash("citizen123"),
                    role="citizen",
                    full_name="John Doe"
                )
            ]
            db.add_all(users)
            db.commit()

        # 2. Seed Assets
        if db.query(Asset).count() == 0:
            print("Seeding Assets...")
            assets = [
                Asset(
                    id="bridge_vanguard_01",
                    name="Vanguard Suspension Bridge",
                    type="Bridge",
                    location="Metro Coastal Corridor, Sector 4",
                    owner="Department of Transportation",
                    construction_material="High-Performance Structural Steel & Concrete",
                    age_years=22,
                    gis_latitude=37.8199,
                    gis_longitude=-122.4783,
                    health_score=87.5,
                    rul_months=168.0,
                    status="Healthy",
                    structural_specs={"span_length_meters": 1280, "deck_width_meters": 27, "lanes": 6}
                ),
                Asset(
                    id="dam_horizon_02",
                    name="Horizon Hydroelectric Dam",
                    type="Dam",
                    location="Canyon River Basin",
                    owner="Bureau of Reclamation",
                    construction_material="Arch Gravity Concrete",
                    age_years=45,
                    gis_latitude=36.0162,
                    gis_longitude=-114.7377,
                    health_score=78.2,
                    rul_months=114.0,
                    status="Warning",
                    structural_specs={"crest_length_meters": 379, "reservoir_capacity_m3": 35000000, "megawatts": 2080}
                ),
                Asset(
                    id="grid_helios_03",
                    name="Helios Substation 4B",
                    type="PowerGrid",
                    location="West Valley Distribution Hub",
                    owner="Federal Energy Grid Commission",
                    construction_material="Copper & Composite Alloys",
                    age_years=12,
                    gis_latitude=34.0522,
                    gis_longitude=-118.2437,
                    health_score=92.1,
                    rul_months=180.0,
                    status="Healthy",
                    structural_specs={"transformer_capacity_mva": 500, "voltage_kv": 500, "cooling_type": "Oil-Forced"}
                ),
                Asset(
                    id="pipeline_hyperion_04",
                    name="Hyperion Gas Pipeline",
                    type="Pipeline",
                    location="Northern Plains Transit Route",
                    owner="Energy Transport Alliance",
                    construction_material="API 5L Grade X70 Carbon Steel",
                    age_years=28,
                    gis_latitude=41.8781,
                    gis_longitude=-87.6298,
                    health_score=64.8,
                    rul_months=48.0,
                    status="Critical",
                    structural_specs={"diameter_inches": 36, "max_pressure_psi": 1200, "length_km": 420}
                ),
                Asset(
                    id="tunnel_summit_05",
                    name="Summit Alpine Highway Tunnel",
                    type="Tunnel",
                    location="Interstate Pass Route 80",
                    owner="State Highway Authority",
                    construction_material="Reinforced Rock Bolt Concrete Shotcrete",
                    age_years=35,
                    gis_latitude=39.2638,
                    gis_longitude=-120.3124,
                    health_score=81.3,
                    rul_months=132.0,
                    status="Healthy",
                    structural_specs={"tunnel_length_meters": 3100, "ventilation_fans": 12, "emergency_escapes": 5}
                ),
                Asset(
                    id="railway_metro_06",
                    name="Metro Line A Transit Track",
                    type="Railway",
                    location="Downtown Loop Terminal",
                    owner="Metropolitan Transit District",
                    construction_material="Continuous Welded Rail Steel",
                    age_years=8,
                    gis_latitude=40.7128,
                    gis_longitude=-74.0060,
                    health_score=94.5,
                    rul_months=210.0,
                    status="Healthy",
                    structural_specs={"track_gauge_mm": 1435, "third_rail_voltage": 750, "average_headway_min": 4}
                ),
                Asset(
                    id="airport_nova_07",
                    name="Nova International Runway 9L",
                    type="Airport",
                    location="Nova Metropolitan Airport",
                    owner="Federal Aviation Administration",
                    construction_material="Polymer-Modified Asphalt Concrete",
                    age_years=15,
                    gis_latitude=25.7906,
                    gis_longitude=-80.2826,
                    health_score=89.0,
                    rul_months=144.0,
                    status="Healthy",
                    structural_specs={"runway_length_meters": 3350, "pavement_classification_number": 85, "width_meters": 45}
                ),
                Asset(
                    id="port_centurion_08",
                    name="Centurion Deepwater Container Port",
                    type="Ports",
                    location="Atlantic Shipping Terminal 1",
                    owner="Port Authority Systems",
                    construction_material="Prestressed Concrete Pile Girders",
                    age_years=19,
                    gis_latitude=32.7765,
                    gis_longitude=-79.9309,
                    health_score=83.2,
                    rul_months=120.0,
                    status="Healthy",
                    structural_specs={"berth_depth_meters": 16, "gantry_cranes": 8, "total_wharf_length_meters": 850}
                ),
                Asset(
                    id="tower_orion_09",
                    name="Orion Telecom Tower 12",
                    type="Telecommunication Towers",
                    location="Hilltop Ridge Broadcast Site",
                    owner="Global Telecom Networks",
                    construction_material="Galvanized Steel Lattice",
                    age_years=5,
                    gis_latitude=39.7392,
                    gis_longitude=-104.9903,
                    health_score=97.8,
                    rul_months=240.0,
                    status="Healthy",
                    structural_specs={"structure_height_meters": 120, "antennas_mounted": 24, "backup_generator_kva": 45}
                )
            ]
            db.add_all(assets)
            db.commit()

            # 3. Seed Telemetry
            print("Seeding Sensor Telemetry...")
            now = datetime.datetime.utcnow()
            for asset in assets:
                metrics = []
                if asset.type == "Bridge":
                    metrics = [
                        ("vibration", 0.05, 0.45),      # mm/s
                        ("load", 12.0, 75.0),           # tons
                        ("strain", 100.0, 450.0),       # microstrain
                        ("wind_speed", 5.0, 45.0)        # km/h
                    ]
                elif asset.type == "Dam":
                    metrics = [
                        ("water_level", 185.0, 202.0),  # meters
                        ("water_pressure", 2500.0, 3200.0), # kPa
                        ("vibration", 0.01, 0.15),
                        ("seepage_rate", 2.0, 8.5)      # L/s
                    ]
                elif asset.type == "PowerGrid":
                    metrics = [
                        ("voltage", 485.0, 515.0),      # kV
                        ("current", 200.0, 850.0),      # Amperes
                        ("temperature", 45.0, 95.0),    # Celsius
                        ("frequency", 59.8, 60.2)       # Hz
                    ]
                elif asset.type == "Pipeline":
                    metrics = [
                        ("pressure", 700.0, 1150.0),    # psi
                        ("flow_rate", 120.0, 180.0),    # L/s
                        ("temperature", 15.0, 32.0),
                        ("gas_leak_ppm", 0.0, 450.0)    # ppm (anomaly if high)
                    ]
                elif asset.type == "Tunnel":
                    metrics = [
                        ("carbon_monoxide", 2.0, 45.0), # ppm
                        ("vibration", 0.02, 0.35),
                        ("traffic_count", 10.0, 250.0), # vehicles/min
                        ("humidity", 40.0, 85.0)
                    ]
                else:  # Generic fallback
                    metrics = [
                        ("vibration", 0.05, 0.5),
                        ("temperature", 20.0, 50.0),
                        ("load", 10.0, 100.0)
                    ]

                # Generate 50 points of historical telemetry (spanning the last 5 days)
                telemetry_entries = []
                for i in range(50):
                    time_offset = datetime.timedelta(hours=i * 2.4)
                    timestamp = now - time_offset
                    for metric_name, min_v, max_v in metrics:
                        # Introduce a potential anomaly to make pipelines look critical
                        val = random.uniform(min_v, max_v)
                        if asset.type == "Pipeline" and metric_name == "gas_leak_ppm" and i < 5:
                            val = random.uniform(400.0, 950.0) # Anomaly in recent points
                        elif asset.type == "Pipeline" and metric_name == "pressure" and i < 5:
                            val = random.uniform(200.0, 400.0) # Pressure drop
                        
                        telemetry_entries.append(
                            SensorTelemetry(
                                asset_id=asset.id,
                                timestamp=timestamp,
                                metric_name=metric_name,
                                value=val
                            )
                        )
                db.add_all(telemetry_entries)
            db.commit()

        # 4. Seed Maintenance Logs
        if db.query(MaintenanceLog).count() == 0:
            print("Seeding Maintenance Logs...")
            logs = [
                MaintenanceLog(
                    asset_id="pipeline_hyperion_04",
                    description="Emergency pipe patch replacement on Valve Station 18 due to corrosion wear and micro-leaks.",
                    cost=145000.00,
                    action_taken="Welded steel sleeves over affected sections; replaced telemetry flow meter.",
                    maintenance_date=datetime.datetime.utcnow() - datetime.timedelta(days=12),
                    priority="High",
                    status="Completed"
                ),
                MaintenanceLog(
                    asset_id="dam_horizon_02",
                    description="Grouting rehabilitation of left concrete abutment to mitigate micro-seepage.",
                    cost=420000.00,
                    action_taken="Injected high-strength epoxy grout resins into joints.",
                    maintenance_date=datetime.datetime.utcnow() - datetime.timedelta(days=30),
                    priority="High",
                    status="Completed"
                ),
                MaintenanceLog(
                    asset_id="bridge_vanguard_01",
                    description="Routine main cable tension inspection and suspension hanger lubricating grease coat.",
                    cost=28000.00,
                    action_taken="Pending inspection and wire replacement check.",
                    maintenance_date=datetime.datetime.utcnow() + datetime.timedelta(days=15),
                    priority="Medium",
                    status="Scheduled"
                )
            ]
            db.add_all(logs)
            db.commit()

        # 5. Seed Drone Missions
        if db.query(DroneMission).count() == 0:
            print("Seeding Drone Missions...")
            drones = [
                DroneMission(
                    id="drone_sentinel_01",
                    name="Sentinel-1 Quadcopter",
                    battery_pct=88.5,
                    altitude_m=45.0,
                    speed_kmh=32.0,
                    latitude=37.8220,
                    longitude=-122.4770,
                    camera_status="Active",
                    mission_status="Patrolling",
                    current_mission_details="Visual inspection scan of Vanguard Suspension Bridge tower piers.",
                    detection_metadata={"concrete_cracks": 0, "rust_spots": 4, "anomalous_heave": False}
                ),
                DroneMission(
                    id="drone_hawk_02",
                    name="Hawk-Eye Hexacopter",
                    battery_pct=95.0,
                    altitude_m=0.0,
                    speed_kmh=0.0,
                    latitude=36.0150,
                    longitude=-114.7360,
                    camera_status="Active",
                    mission_status="Idle",
                    current_mission_details="Staged at Hoover heliport, ready for dam monitoring dispatch.",
                    detection_metadata={}
                ),
                DroneMission(
                    id="drone_falcon_03",
                    name="Falcon-3 Fixed-Wing",
                    battery_pct=42.0,
                    altitude_m=120.0,
                    speed_kmh=68.0,
                    latitude=41.8790,
                    longitude=-87.6300,
                    camera_status="Recording",
                    mission_status="Emergency Dispatch",
                    current_mission_details="Surveying Pipeline route for thermal anomaly leakage markers.",
                    detection_metadata={"thermal_hotspots": 1, "vegetation_stress": True}
                )
            ]
            db.add_all(drones)
            db.commit()

        # 6. Seed Citizen Reports
        if db.query(CitizenReport).count() == 0:
            print("Seeding Citizen Reports...")
            reports = [
                CitizenReport(
                    reporter_name="Sarah Miller",
                    contact_info="sarah.m@gmail.com",
                    report_type="Pothole",
                    description="Extremely large and deep pothole on the center lane of highway bridge section 4. It forces cars to swerve dangerously.",
                    location="Bridge Parkway East, Lane 2",
                    latitude=37.8210,
                    longitude=-122.4790,
                    status="Investigating",
                    gemini_summary="Citizen Sarah Miller reported a major, hazardous pothole on the center lane of the bridge pathway causing traffic safety risks."
                ),
                CitizenReport(
                    reporter_name="David Cooper",
                    contact_info="david.c@yahoo.com",
                    report_type="Power Failure",
                    description="Massive sparks coming from the substation transformer block during lightning storm followed by complete blackout.",
                    location="Oak Street Substation",
                    latitude=34.0535,
                    longitude=-118.2450,
                    status="Resolved",
                    gemini_summary="Sparks from substation transformer leading to a localized power outage; emergency repair crews successfully resolved the transformer failure."
                )
            ]
            db.add_all(reports)
            db.commit()

        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
