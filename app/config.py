"""
설정 파일
- DB 연결 정보
- 기본 임계값
"""

# MariaDB 연결 정보
DB_URL = "mysql+pymysql://root:1234@localhost:3306/sinker_iot"

# 기본 임계값 설정
DEFAULT_THRESHOLDS = {
    # 토양 수분 임계값
    "moisture_warning": 600.0,
    "moisture_danger": 700.0,
    
    # 진동 센서 임계값
    "vibration_warning": 1.0,
    "vibration_danger": 2.0,
    
    # 가속도 변화량 임계값 (직전 값 대비)
    "accel_delta_warning": 1.0,
    "accel_delta_danger": 2.0,
    
    # 자이로 변화량 임계값 (직전 값 대비)
    "gyro_delta_warning": 5.0,
    "gyro_delta_danger": 10.0
}

# 타임존 설정
TIMEZONE = "Asia/Seoul"
