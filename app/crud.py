"""
CRUD 및 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional
import pytz
import math

from app.models import SensorData, Threshold
from app.schemas import SensorDataCreate
from app.config import TIMEZONE, RiskThresholds


def calculate_risk_level(
    moisture: float,
    accel_x: float,
    accel_y: float,
    vibration_raw: float
) -> int:
    """
    가중치 기반 위험도 계산 (0: 정상, 1: 주의, 2: 위험)
    
    논문 기반 가중치 적용:
    - 기울기 (Tilt): 0.5 - 직접적 전조 (Primary Indicator)
    - 수분 (Moisture): 0.3 - 붕괴 원인 (Secondary Indicator)  
    - 진동 (Vibration): 0.2 - 보조 지표 (Tertiary Indicator)
    
    계산 과정:
    1. 각 센서 값을 0~1로 정규화
    2. 가중치 적용하여 최종 점수 계산
    3. 최종 점수로 위험도 판정
    
    Args:
        moisture: 토양 수분 센서 값 (낮을수록 수분 많음)
        accel_x: X축 가속도
        accel_y: Y축 가속도
        vibration_raw: 진동 센서 값 (0 또는 1)
    
    Returns:
        0: 정상, 1: 주의, 2: 위험
    """
    
    # 1. 기울기 점수 계산 (가속도 X, Y 벡터 크기)
    tilt_magnitude = math.sqrt(accel_x ** 2 + accel_y ** 2)
    
    if tilt_magnitude < RiskThresholds.TILT_NORMAL:
        tilt_score = 0.0
    elif tilt_magnitude < RiskThresholds.TILT_DANGER:
        # 선형 보간: NORMAL → DANGER 구간을 0~1로 정규화
        tilt_score = (tilt_magnitude - RiskThresholds.TILT_NORMAL) / \
                     (RiskThresholds.TILT_DANGER - RiskThresholds.TILT_NORMAL)
    else:
        tilt_score = 1.0
    
    # 2. 수분 점수 계산 (역방향: 낮을수록 위험)
    if moisture > RiskThresholds.MOISTURE_NORMAL:
        moisture_score = 0.0
    elif moisture > RiskThresholds.MOISTURE_WARNING:
        # 선형 보간: NORMAL → WARNING 구간을 0~1로 정규화
        moisture_score = (RiskThresholds.MOISTURE_NORMAL - moisture) / \
                        (RiskThresholds.MOISTURE_NORMAL - RiskThresholds.MOISTURE_WARNING)
    else:
        moisture_score = 1.0
    
    # 3. 진동 점수 계산 (이진 신호)
    vibration_score = 1.0 if vibration_raw >= RiskThresholds.VIBRATION_THRESHOLD else 0.0
    
    # 4. 가중치 적용하여 최종 점수 계산
    final_score = (
        RiskThresholds.WEIGHT_TILT * tilt_score +
        RiskThresholds.WEIGHT_MOISTURE * moisture_score +
        RiskThresholds.WEIGHT_VIBRATION * vibration_score
    )
    
    # 5. 최종 위험도 판정
    if final_score < RiskThresholds.RISK_NORMAL_MAX:
        return 0  # 정상
    elif final_score < RiskThresholds.RISK_WARNING_MAX:
        return 1  # 주의
    else:
        return 2  # 위험


def create_sensor_data(db: Session, data: SensorDataCreate) -> SensorData:
    """
    센서 데이터 생성 및 저장
    
    Args:
        db: 데이터베이스 세션
        data: 센서 데이터 (Pydantic 스키마)
    
    Returns:
        저장된 센서 데이터 (ORM 모델)
    """
    # 위험도 계산
    risk_level = calculate_risk_level(
        moisture=data.moisture,
        accel_x=data.accel.x,
        accel_y=data.accel.y,
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
    
    Args:
        db: 데이터베이스 세션
        minutes: 최근 N분 데이터
        start: 시작 시각
        end: 종료 시각
        limit: 최대 조회 개수
    
    Returns:
        센서 데이터 리스트 (최신순)
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
    모든 임계값 조회 (레거시 지원용)
    """
    return db.query(Threshold).all()


def upsert_threshold(db: Session, name: str, value: float) -> Threshold:
    """
    임계값 업데이트 또는 생성 (레거시 지원용)
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
