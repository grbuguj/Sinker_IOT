"""
SQLAlchemy ORM 모델 정의
"""
from sqlalchemy import Column, BigInteger, Integer, Float, DateTime, String, Index
from sqlalchemy.sql import func
from app.database import Base


class SensorData(Base):
    """
    센서 데이터 테이블
    """
    __tablename__ = "sensor_data"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 토양 수분
    moisture = Column(Float, nullable=False)
    
    # 가속도 센서 (3축)
    accel_x = Column(Float, nullable=False)
    accel_y = Column(Float, nullable=False)
    accel_z = Column(Float, nullable=False)
    
    # 자이로 센서 (3축)
    gyro_x = Column(Float, nullable=False)
    gyro_y = Column(Float, nullable=False)
    gyro_z = Column(Float, nullable=False)
    
    # 진동 센서
    vibration_raw = Column(Float, nullable=False)
    
    # 위험도 (0: 정상, 1: 주의, 2: 위험)
    risk_level = Column(Integer, nullable=False, default=0)
    
    # 생성 시각 (한국 시간)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 인덱스 생성 (조회 성능 향상)
    __table_args__ = (
        Index('idx_created_at', 'created_at'),
    )


class Threshold(Base):
    """
    임계값 설정 테이블
    """
    __tablename__ = "thresholds"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    value = Column(Float, nullable=False)
