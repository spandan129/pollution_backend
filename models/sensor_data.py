from pydantic import BaseModel

class SensorData(BaseModel):
    sensor_id: str
    timestamp: str
    air_quality_index: int
    water_quality_index: int
    ph_level: float