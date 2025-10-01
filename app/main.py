from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from sqlmodel import select
from .models import SensorData, SensorDataCreate, SensorDataUpdate, ArduinoSensorData, WateringData, WateringDataUpdate
from .db import init_db, get_session
from datetime import datetime
import os

app = FastAPI(title="Pi Sensor Data Backend", version="1.0.0")

# Create DB tables at startup
@app.on_event("startup")
def on_startup():
    init_db()

# Static + templates for the tiny frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ------------------ HTML Page ------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ------------------ API ------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}

from sqlmodel import Session

def session_dep():
    with get_session() as s:
        yield s


# ------------------ Sensor Data API ------------------
@app.post("/api/v1/sensor-data", response_model=SensorData, status_code=201)
def create_sensor_data(payload: ArduinoSensorData, request: Request, session: Session = Depends(session_dep)):
    # Use device_id from payload, fallback to header for backward compatibility
    device_id = payload.device_id or request.headers.get("X-Device-ID")
    
    # Convert Arduino field names to our database field names
    sensor_data = SensorData(
        temperature=payload.temperature,
        humidity=payload.humidity,
        lux=payload.lux,
        pump_active=payload.pumpActive,
        timestamp=payload.timestamp,
        device_id=device_id,
        firmware_version=payload.firmware_version,
        sensor_type=payload.sensor_type
    )
    
    session.add(sensor_data)
    session.commit()
    session.refresh(sensor_data)
    return sensor_data

@app.get("/api/sensor-data", response_model=List[SensorData])
def list_sensor_data(session: Session = Depends(session_dep), limit: Optional[int] = 100):
    stmt = select(SensorData).order_by(SensorData.created_at.desc()).limit(limit)
    return session.exec(stmt).all()

@app.get("/api/sensor-data/{sensor_id}", response_model=SensorData)
def get_sensor_data(sensor_id: int, session: Session = Depends(session_dep)):
    sensor_data = session.get(SensorData, sensor_id)
    if not sensor_data:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    return sensor_data

@app.put("/api/sensor-data/{sensor_id}", response_model=SensorData)
def update_sensor_data(sensor_id: int, payload: SensorDataUpdate, session: Session = Depends(session_dep)):
    sensor_data = session.get(SensorData, sensor_id)
    if not sensor_data:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(sensor_data, k, v)
    session.add(sensor_data)
    session.commit()
    session.refresh(sensor_data)
    return sensor_data

@app.delete("/api/sensor-data/{sensor_id}", status_code=204)
def delete_sensor_data(sensor_id: int, session: Session = Depends(session_dep)):
    sensor_data = session.get(SensorData, sensor_id)
    if not sensor_data:
        raise HTTPException(status_code=404, detail="Sensor data not found")
    session.delete(sensor_data)
    session.commit()
    return

# ------------------ Watering Data API ------------------
@app.get("/api/watering", response_model=WateringData)
def get_watering_data(session: Session = Depends(session_dep)):
    watering_data = session.get(WateringData, 1)
    if not watering_data:
        # Create default watering data if it doesn't exist
        watering_data = WateringData()
        session.add(watering_data)
        session.commit()
        session.refresh(watering_data)
    return watering_data

@app.put("/api/watering", response_model=WateringData)
def update_watering_data(payload: WateringDataUpdate, session: Session = Depends(session_dep)):
    watering_data = session.get(WateringData, 1)
    if not watering_data:
        # Create new watering data if it doesn't exist
        watering_data = WateringData()
        session.add(watering_data)
        session.commit()
        session.refresh(watering_data)
    
    # Update fields
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(watering_data, k, v)
    
    # Update the updated_at timestamp
    watering_data.updated_at = datetime.utcnow()
    
    session.add(watering_data)
    session.commit()
    session.refresh(watering_data)
    return watering_data