from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class ArduinoSensorData(BaseModel):
    """Model to receive Arduino data with original field names"""
    temperature: float
    humidity: float
    lux: float  # Changed from int to float to handle decimal values
    pumpActive: bool
    timestamp: int  # Changed from lastReading to timestamp
    device_id: str  # Now included in payload instead of header
    firmware_version: Optional[str] = None
    sensor_type: Optional[str] = None

class SensorDataBase(SQLModel):
    temperature: float = Field(description="Temperature reading")
    humidity: float = Field(description="Humidity reading")
    lux: float = Field(description="Light level in lux")  # Changed to float
    pump_active: bool = Field(description="Pump status")
    timestamp: int = Field(description="Device timestamp")  # Changed from last_reading
    device_id: Optional[str] = Field(default=None, max_length=50, description="Device identifier")
    firmware_version: Optional[str] = Field(default=None, max_length=20, description="Firmware version")
    sensor_type: Optional[str] = Field(default=None, max_length=50, description="Sensor type")

class SensorData(SensorDataBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class SensorDataCreate(SensorDataBase):
    pass

class SensorDataUpdate(SQLModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    lux: Optional[float] = None  # Changed to float
    pump_active: Optional[bool] = None
    timestamp: Optional[int] = None  # Changed from last_reading
    device_id: Optional[str] = None
    firmware_version: Optional[str] = None
    sensor_type: Optional[str] = None
