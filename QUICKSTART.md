# 🚀 IoT 싱크홀 경보 시스템 - 빠른 시작 가이드

## ✅ 설치 완료 확인

프로젝트가 성공적으로 생성되었습니다!

```
app/
├── __init__.py              # ✅ 패키지 초기화
├── main.py                  # ✅ FastAPI 메인 앱
├── config.py                # ✅ 설정 (DB, 임계값)
├── database.py              # ✅ DB 연결 관리
├── models.py                # ✅ SQLAlchemy ORM
├── schemas.py               # ✅ Pydantic 스키마
├── crud.py                  # ✅ 비즈니스 로직
├── websocket_manager.py     # ✅ WebSocket 관리
├── templates/               # ✅ HTML 템플릿
│   ├── index.html           # ✅ 실시간 대시보드
│   ├── history.html         # ✅ 이력 조회
│   └── config.html          # ✅ 임계값 설정
└── static/                  # ✅ 정적 파일
    ├── css/
    │   └── style.css        # ✅ 스타일시트
    └── js/
        ├── dashboard.js     # ✅ 대시보드 JS
        ├── history.js       # ✅ 이력 JS
        └── config.js        # ✅ 설정 JS
```

## 🎯 실행 방법 (3단계)

### 1단계: 패키지 설치

```bash
pip install -r requirements.txt
```

### 2단계: MariaDB 확인

데이터베이스 `sinker_iot`가 존재하는지 확인:

```bash
mysql -u root -p1234 -e "SHOW DATABASES LIKE 'sinker_iot';"
```

없다면 생성:

```bash
mysql -u root -p1234 -e "CREATE DATABASE sinker_iot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 3단계: 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 접속하기

서버 실행 후:

- **실시간 대시보드**: http://localhost:8000/
- **이력 조회**: http://localhost:8000/history
- **임계값 설정**: http://localhost:8000/config
- **API 문서**: http://localhost:8000/docs

## 🧪 테스트하기

새 터미널에서 테스트 스크립트 실행:

```bash
python test_sensor.py
```

이 스크립트는 3초마다 랜덤 센서 데이터를 서버에 전송합니다.
실시간 대시보드에서 그래프가 업데이트되는 것을 확인하세요!

## 📊 주요 기능

### 1. 실시간 대시보드 (/)
- ✅ WebSocket 실시간 연결
- ✅ 3개 그래프 (토양 수분, 진동, 기울기)
- ✅ 최근 50개 데이터 포인트 표시
- ✅ 위험도 배지 (정상/주의/위험)
- ✅ 9개 센서 값 실시간 표시

### 2. 이력 조회 (/history)
- ✅ 시간대별 필터 (10분, 1시간, 6시간, 오늘)
- ✅ 테이블 형태로 표시
- ✅ CSV 다운로드 기능

### 3. 임계값 설정 (/config)
- ✅ 8개 임계값 실시간 수정
- ✅ 토스트 알림
- ✅ DB에 즉시 반영

## 🎨 위험도 계산 로직

```
위험도 = max(
    토양수분_위험도,
    진동_위험도,
    가속도변화_위험도,
    자이로변화_위험도
)
```

각 센서별:
- 위험 임계값 초과 → 2 (위험)
- 주의 임계값 초과 → 1 (주의)
- 정상 → 0 (정상)

## 🔧 설정 변경

### DB 연결 변경
`app/config.py` 파일 수정:

```python
DB_URL = "mysql+pymysql://사용자:비번@호스트:포트/DB이름"
```

### 임계값 변경
웹 UI (`/config`)에서 변경하거나
`app/config.py`의 `DEFAULT_THRESHOLDS` 수정

### 포트 변경
```bash
uvicorn app.main:app --reload --port 8080
```

## 🐛 문제 해결

### 1. MariaDB 연결 오류
```bash
# 서비스 상태 확인
sudo systemctl status mariadb

# 시작
sudo systemctl start mariadb
```

### 2. 포트 사용 중
다른 포트 사용:
```bash
uvicorn app.main:app --reload --port 8080
```

### 3. 모듈 import 오류
프로젝트 루트에서 실행하는지 확인:
```bash
pwd  # /Users/jaeung/Sinker_IOT 여야 함
```

### 4. WebSocket 연결 안됨
방화벽 확인 또는 브라우저 콘솔 확인

## 📡 센서 데이터 전송 예시

### Python
```python
import requests
from datetime import datetime

data = {
    "moisture": 450.5,
    "accel": {"x": 0.05, "y": -0.03, "z": 9.80},
    "gyro": {"x": 0.02, "y": -0.01, "z": 0.00},
    "vibration_raw": 3.2,
    "timestamp": datetime.now().isoformat()
}

response = requests.post("http://localhost:8000/sensor", json=data)
print(response.json())
```

### curl
```bash
curl -X POST "http://localhost:8000/sensor" \
  -H "Content-Type: application/json" \
  -d '{
    "moisture": 450.5,
    "accel": {"x": 0.05, "y": -0.03, "z": 9.80},
    "gyro": {"x": 0.02, "y": -0.01, "z": 0.00},
    "vibration_raw": 3.2,
    "timestamp": "2025-11-19T12:30:05"
  }'
```

## 🎉 완료!

이제 시스템이 준비되었습니다!

1. ✅ 서버 실행: `uvicorn app.main:app --reload`
2. ✅ 브라우저 접속: http://localhost:8000/
3. ✅ 테스트: `python test_sensor.py`

문제가 있으면 README.md를 참고하세요!
