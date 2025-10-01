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
    timestamp: Optional[float] = None  # Changed from last_reading
    device_id: Optional[str] = None
    firmware_version: Optional[str] = None
    sensor_type: Optional[str] = None

# Watering Data Model
class WateringData(SQLModel, table=True):
    device_id: str = Field(primary_key=True, description="Device identifier")
    pump_active: bool = Field(default=False, description="Current pump status")
    last_watering: Optional[datetime] = Field(default=None, description="Last watering time")
    watering_duration: int = Field(default=30, description="Watering duration in seconds")
    auto_watering: bool = Field(default=True, description="Auto watering enabled")
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="Last update timestamp")

class WateringDataUpdate(SQLModel):
    pump_active: Optional[bool] = None
    last_watering: Optional[datetime] = None
    watering_duration: Optional[int] = None
    auto_watering: Optional[bool] = None
    device_id: Optional[str] = None
    timestamp: Optional[float] = None

# Watering History Model
class WateringHistoryBase(SQLModel):
    device_id: str = Field(max_length=50, description="Device identifier")
    watering_duration: int = Field(description="Duration of watering in seconds")
    auto_watering: bool = Field(description="Whether watering was automatic")
    watering_started: datetime = Field(description="When watering started")
    watering_ended: Optional[datetime] = Field(default=None, description="When watering ended")

class WateringHistory(WateringHistoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class WateringHistoryCreate(WateringHistoryBase):
    pass

class WateringHistoryUpdate(SQLModel):
    watering_ended: Optional[datetime] = None
