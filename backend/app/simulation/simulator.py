import math
import datetime
from sqlalchemy.orm import Session
from app.models.models import Asset, DisasterSimulation
from app.schemas.schemas import SimulationRequest, SimulationResponse, AssetResponse

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance in kilometers between two points on the sphere.
    """
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def run_disaster_simulation(db: Session, req: SimulationRequest) -> SimulationResponse:
    # 1. Fetch all assets from DB
    all_assets = db.query(Asset).all()
    affected_assets = []
    
    # 2. Identify assets in impact radius
    for asset in all_assets:
        dist = haversine_distance(req.gis_latitude, req.gis_longitude, asset.gis_latitude, asset.gis_longitude)
        if dist <= req.radius_km:
            affected_assets.append((asset, dist))
            
    # 3. Compute impact heuristics
    # Intensity factors: Earthquakes (Richter 5-9), Cyclone (Cat 1-5), Others (0-1)
    intensity_scale = req.intensity
    if req.disaster_type == "Earthquake":
        # Normalize Richter scale from 5.0 to 9.0
        severity_ratio = max(0.1, min(1.0, (intensity_scale - 5.0) / 4.0))
    elif req.disaster_type == "Cyclone":
        # Normalize category from 1 to 5
        severity_ratio = max(0.2, min(1.0, intensity_scale / 5.0))
    else:
        severity_ratio = max(0.1, min(1.0, intensity_scale))
        
    num_affected = len(affected_assets)
    
    # Heuristics for economic loss, population impact and repair costs
    base_population_factor = 25000 # people per km2 impacted in typical smart city sectors
    population_impacted = int(math.pi * (req.radius_km**2) * base_population_factor * severity_ratio * 0.1)
    if num_affected == 0:
        population_impacted = int(population_impacted * 0.05)
        
    economic_loss = 0.0
    repair_cost = 0.0
    response_timeline = 1.0 + (req.radius_km * 0.5) + (severity_ratio * 15.0)
    
    asset_responses = []
    
    for asset, dist in affected_assets:
        # Distance decay factor: closer assets take more damage
        distance_decay = 1.0 - (dist / max(1.0, req.radius_km))
        damage_coef = severity_ratio * distance_decay
        
        # Calculate impact depending on asset type
        asset_base_val = 50.0 # millions
        if asset.type == "Bridge":
            asset_base_val = 180.0
            vulnerability = 0.8 if req.disaster_type in ["Earthquake", "Bridge Collapse"] else 0.3
        elif asset.type == "Dam":
            asset_base_val = 350.0
            vulnerability = 0.9 if req.disaster_type in ["Earthquake", "Dam Breach"] else 0.2
        elif asset.type == "PowerGrid":
            asset_base_val = 90.0
            vulnerability = 0.85 if req.disaster_type in ["Cyclone", "Power Outage"] else 0.4
        elif asset.type == "Pipeline":
            asset_base_val = 120.0
            vulnerability = 0.9 if req.disaster_type in ["Earthquake", "Chemical Leak"] else 0.1
        else:
            vulnerability = 0.5
            
        asset_damage = asset_base_val * damage_coef * vulnerability
        repair_cost += asset_damage
        economic_loss += asset_damage * 3.5 # multiplier for business disruption
        
        # Degrade health score for the affected assets temporarily in the response (does not save to DB to avoid mutating registry unless confirmed)
        simulated_health = max(10.0, asset.health_score - (damage_coef * vulnerability * 100.0))
        simulated_status = "Critical" if simulated_health < 50.0 else ("Warning" if simulated_health < 80.0 else "Healthy")
        
        asset_responses.append(
            AssetResponse(
                id=asset.id,
                name=asset.name,
                type=asset.type,
                location=asset.location,
                owner=asset.owner,
                construction_material=asset.construction_material,
                age_years=asset.age_years,
                gis_latitude=asset.gis_latitude,
                gis_longitude=asset.gis_longitude,
                health_score=round(simulated_health, 1),
                rul_months=round(max(0.0, asset.rul_months * (simulated_health / 100.0)), 1),
                status=simulated_status,
                structural_specs=asset.structural_specs,
                created_at=asset.created_at,
                updated_at=asset.updated_at
            )
        )
        
    # Cap values
    economic_loss = round(max(0.1, economic_loss), 2)
    repair_cost = round(max(0.05, repair_cost), 2)
    response_timeline = round(response_timeline, 1)
    
    # Save simulation history to DB
    affected_ids = [a[0].id for a in affected_assets]
    sim_record = DisasterSimulation(
        disaster_type=req.disaster_type,
        severity=severity_ratio,
        economic_loss_millions=economic_loss,
        population_impacted=population_impacted,
        affected_assets_ids=affected_ids,
        response_days=response_timeline,
        repair_cost_millions=repair_cost,
        simulation_time=datetime.datetime.utcnow()
    )
    db.add(sim_record)
    db.commit()
    
    # Create text report summary
    summary = f"Disaster impact assessment report for a simulated {req.disaster_type} (Intensity: {req.intensity}) " \
              f"centered at Coordinates [{req.gis_latitude}, {req.gis_longitude}] with impact radius {req.radius_km}km. " \
              f"A total of {len(affected_assets)} critical infrastructure assets are within the damage perimeter. " \
              f"Estimated economic disruption is valued at ${economic_loss}M, with direct repair expenditures of ${repair_cost}M. " \
              f"Impacted regional population is estimated at {population_impacted:,} citizens. " \
              f"Projected emergency recovery timeline is {response_timeline} days."
              
    return SimulationResponse(
        disaster_type=req.disaster_type,
        gis_latitude=req.gis_latitude,
        gis_longitude=req.gis_longitude,
        radius_km=req.radius_km,
        intensity=req.intensity,
        economic_loss_millions=economic_loss,
        population_impacted=population_impacted,
        affected_assets=asset_responses,
        repair_cost_millions=repair_cost,
        response_timeline_days=response_timeline,
        evacuation_recommended=bool(severity_ratio > 0.5 and len(affected_assets) > 0),
        summary_report=summary
    )
