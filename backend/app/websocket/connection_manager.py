import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List

from app.config.database import SessionLocal
from app.sensors.sensor_engine import stream_sensor_telemetry, get_latest_telemetry_dict
from app.models.models import Asset

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Connection might have died
                pass

manager = ConnectionManager()

@router.websocket("/ws/sensors/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    db: Session = SessionLocal()
    try:
        while True:
            # Generate new telemetry
            stream_sensor_telemetry(db)
            
            # Fetch latest data for all assets
            assets = db.query(Asset).all()
            data = []
            for asset in assets:
                telemetry = get_latest_telemetry_dict(db, asset.id)
                data.append({
                    "asset_id": asset.id,
                    "asset_name": asset.name,
                    "asset_type": asset.type,
                    "status": asset.status,
                    "health_score": asset.health_score,
                    "telemetry": telemetry
                })
                
            await websocket.send_text(json.dumps(data))
            # Wait 2 seconds before streaming the next update
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        manager.disconnect(websocket)
    finally:
        db.close()
