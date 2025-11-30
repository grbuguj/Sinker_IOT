"""
설정 파일
- DB 연결 정보
- 위험도 계산 임계값 (논문 기반)
"""

# MariaDB 연결 정보
DB_URL = "mysql+pymysql://root:1234@localhost:3306/sinker_iot"

# 타임존 설정
TIMEZONE = "Asia/Seoul"


# ============================================
# 위험도 계산 임계값 (실험 데이터 기반)
# ============================================

class RiskThresholds:
    """
    싱크홀 위험도 판정 임계값
    
    기울기 (Tilt): 가속도 X, Y 축의 벡터 크기 sqrt(x² + y²)
    수분 (Moisture): 저항식 센서 (값이 낮을수록 수분 많음)
    진동 (Vibration): 디지털 신호 (0 또는 1)
    """
    
    # 기울기 임계값 (센서 평상시 값 기준 조정)
    TILT_NORMAL = 6.0    # 정상 기준 (평상시 5.7 → 여유 두고 6.0)
    TILT_DANGER = 8.0    # 위험 기준 (확실한 변화 감지)
    
    # 수분 임계값 (역방향: 낮을수록 수분 많음)
    MOISTURE_NORMAL = 800   # 정상 (건조~적정)
    MOISTURE_WARNING = 750  # 주의 (수분 증가)
    MOISTURE_DANGER = 750   # 위험 (침수/포화) - WARNING과 동일선상
    
    # 진동 임계값 (이진 신호)
    VIBRATION_THRESHOLD = 1.0  # 1이면 진동 감지
    
    # 가중치 (논문 기반)
    WEIGHT_TILT = 0.5      # 직접적 전조 (Primary Indicator)
    WEIGHT_MOISTURE = 0.3  # 붕괴 원인 (Secondary Indicator)
    WEIGHT_VIBRATION = 0.2 # 보조 지표 (Tertiary Indicator)
    
    # 최종 위험도 판정 임계값
    RISK_NORMAL_MAX = 0.3   # < 0.3: 정상
    RISK_WARNING_MAX = 0.6  # 0.3~0.6: 주의
    # >= 0.6: 위험


# 레거시 호환용 (DB 초기화에 사용, 실제 계산엔 안 씀)
DEFAULT_THRESHOLDS = {
    "moisture_warning": 750.0,
    "moisture_danger": 800.0,
    "vibration_warning": 1.0,
    "vibration_danger": 1.0,
    "accel_delta_warning": 6.0,
    "accel_delta_danger": 8.0,
    "gyro_delta_warning": 0.0,
    "gyro_delta_danger": 0.0,
}
