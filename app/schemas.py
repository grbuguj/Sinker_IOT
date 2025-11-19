"""
Pydantic 스키마 정의
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AccelData(BaseModel):
    """가속도 센서 데이터"""
    x: float
    y: float
    z: float


class GyroData(BaseModel):
    """자이로 센서 데이터"""
    x: float
    y: float
    z: float


class SensorDataCreate(BaseModel):
    """센서 데이터 생성 요청"""
    moisture: float = Field(..., description="토양 수분값")
    accel: AccelData = Field(..., description="3축 가속도")
    gyro: GyroData = Field(..., description="3축 자이로")
    vibration_raw: float = Field(..., description="진동 센서 raw 값")
    timestamp: Optional[str] = Field(None, description="센서 측 타임스탬프")


class SensorDataRead(BaseModel):
    """센서 데이터 응답"""
    id: int
    moisture: float
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    vibration_raw: float
    risk_level: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ThresholdRead(BaseModel):
    """임계값 조회 응답"""
    id: int
    name: str
    value: float
    
    class Config:
        from_attributes = True


class ThresholdUpdate(BaseModel):
    """임계값 업데이트 요청"""
    name: str = Field(..., description="임계값 이름")
    value: float = Field(..., description="임계값")
