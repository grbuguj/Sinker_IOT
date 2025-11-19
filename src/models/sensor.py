from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from .db import Base

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    moisture = Column(Float, nullable=False)   # 수분센서
    tilt = Column(Float, nullable=False)       # 기울기센서
    vibration = Column(Float, nullable=False)  # 진동센서
    created_at = Column(DateTime(timezone=True), server_default=func.now())
