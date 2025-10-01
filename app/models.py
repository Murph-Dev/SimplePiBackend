from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class ArduinoSensorData(BaseModel):
    """Model to receive Arduino data with original field names"""
    temperature: float
    humidity: float
    lux: int
    pumpActive: bool
    lastReading: int

class SensorDataBase(SQLModel):
    temperature: float = Field(description="Temperature reading")
    humidity: float = Field(description="Humidity reading")
    lux: int = Field(description="Light level in lux")
    pump_active: bool = Field(description="Pump status")
    last_reading: int = Field(description="Last reading timestamp")
    device_id: Optional[str] = Field(default=None, max_length=50, description="Device identifier")

class SensorData(SensorDataBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class SensorDataCreate(SensorDataBase):
    pass

class SensorDataUpdate(SQLModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    lux: Optional[int] = None
    pump_active: Optional[bool] = None
    last_reading: Optional[int] = None
    device_id: Optional[str] = None
