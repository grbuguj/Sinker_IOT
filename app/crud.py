"""
CRUD 및 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import pytz
from app.models import SensorData, Threshold
from app.schemas import SensorDataCreate
from app.config import TIMEZONE


def get_thresholds(db: Session) -> Dict[str, float]:
    """
    모든 임계값을 딕셔너리로 반환
    """
    thresholds = db.query(Threshold).all()
    return {t.name: t.value for t in thresholds}


def calculate_risk_level(
    db: Session,
    moisture: float,
    accel_x: float, accel_y: float, accel_z: float,
    gyro_x: float, gyro_y: float, gyro_z: float,
    vibration_raw: float
) -> int:
    """
    위험도 계산 (0: 정상, 1: 주의, 2: 위험)
    
    - moisture 기준
    - vibration_raw 기준
    - accel 변화량 기준 (직전 값 대비)
    - gyro 변화량 기준 (직전 값 대비)
    
    위 4가지 중 가장 높은 위험도를 반환
    """
    thresholds = get_thresholds(db)
    
    # 1) 토양 수분 위험도
    moisture_risk = 0
    if moisture >= thresholds.get("moisture_danger", 700.0):
        moisture_risk = 2
    elif moisture >= thresholds.get("moisture_warning", 600.0):
        moisture_risk = 1
    
    # 2) 진동 위험도
    vibration_risk = 0
    if vibration_raw >= thresholds.get("vibration_danger", 2.0):
        vibration_risk = 2
    elif vibration_raw >= thresholds.get("vibration_warning", 1.0):
        vibration_risk = 1
    
    # 3) 가속도 변화량 위험도
    accel_risk = 0
    prev_data = db.query(SensorData).order_by(desc(SensorData.id)).first()
    if prev_data:
        delta_x = abs(accel_x - prev_data.accel_x)
        delta_y = abs(accel_y - prev_data.accel_y)
        delta_z = abs(accel_z - prev_data.accel_z)
        max_delta = max(delta_x, delta_y, delta_z)
        
        if max_delta >= thresholds.get("accel_delta_danger", 2.0):
            accel_risk = 2
        elif max_delta >= thresholds.get("accel_delta_warning", 1.0):
            accel_risk = 1
    
    # 4) 자이로 변화량 위험도
    gyro_risk = 0
    if prev_data:
        delta_x = abs(gyro_x - prev_data.gyro_x)
        delta_y = abs(gyro_y - prev_data.gyro_y)
        delta_z = abs(gyro_z - prev_data.gyro_z)
        max_delta = max(delta_x, delta_y, delta_z)
        
        if max_delta >= thresholds.get("gyro_delta_danger", 10.0):
            gyro_risk = 2
        elif max_delta >= thresholds.get("gyro_delta_warning", 5.0):
            gyro_risk = 1
    
    # 최종 위험도: 4가지 중 최댓값
    return max(moisture_risk, vibration_risk, accel_risk, gyro_risk)


def create_sensor_data(db: Session, data: SensorDataCreate) -> SensorData:
    """
    센서 데이터 생성 및 저장
    """
    # 위험도 계산
    risk_level = calculate_risk_level(
        db=db,
        moisture=data.moisture,
        accel_x=data.accel.x,
        accel_y=data.accel.y,
        accel_z=data.accel.z,
        gyro_x=data.gyro.x,
        gyro_y=data.gyro.y,
        gyro_z=data.gyro.z,
        vibration_raw=data.vibration_raw
    )
    
    # 타임스탬프 처리 (한국 시간)
    kst = pytz.timezone(TIMEZONE)
    if data.timestamp:
        try:
            created_at = datetime.fromisoformat(data.timestamp.replace('Z', '+00:00'))
            created_at = created_at.astimezone(kst)
        except:
            created_at = datetime.now(kst)
    else:
        created_at = datetime.now(kst)
    
    # DB 저장
    db_data = SensorData(
        moisture=data.moisture,
        accel_x=data.accel.x,
        accel_y=data.accel.y,
        accel_z=data.accel.z,
        gyro_x=data.gyro.x,
        gyro_y=data.gyro.y,
        gyro_z=data.gyro.z,
        vibration_raw=data.vibration_raw,
        risk_level=risk_level,
        created_at=created_at
    )
    
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    
    return db_data


def get_latest_sensor_data(db: Session) -> Optional[SensorData]:
    """
    최신 센서 데이터 1건 조회
    """
    return db.query(SensorData).order_by(desc(SensorData.id)).first()


def get_sensor_history(
    db: Session,
    minutes: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 200
) -> List[SensorData]:
    """
    센서 데이터 이력 조회
    
    - minutes: 최근 N분 데이터
    - start/end: 특정 기간 데이터
    - 둘 다 없으면 최근 limit개 반환
    """
    query = db.query(SensorData)
    
    if minutes:
        kst = pytz.timezone(TIMEZONE)
        cutoff_time = datetime.now(kst) - timedelta(minutes=minutes)
        query = query.filter(SensorData.created_at >= cutoff_time)
    elif start and end:
        query = query.filter(SensorData.created_at.between(start, end))
    
    return query.order_by(desc(SensorData.created_at)).limit(limit).all()


def get_all_thresholds(db: Session) -> List[Threshold]:
    """
    모든 임계값 조회
    """
    return db.query(Threshold).all()


def upsert_threshold(db: Session, name: str, value: float) -> Threshold:
    """
    임계값 업데이트 또는 생성
    """
    threshold = db.query(Threshold).filter(Threshold.name == name).first()
    
    if threshold:
        threshold.value = value
    else:
        threshold = Threshold(name=name, value=value)
        db.add(threshold)
    
    db.commit()
    db.refresh(threshold)
    
    return threshold
