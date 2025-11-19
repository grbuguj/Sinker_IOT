# IoT 기반 소규모 싱크홀 조기 경보 시스템

FastAPI + MariaDB + WebSocket + Jinja2 + Chart.js를 사용한 실시간 센서 데이터 모니터링 시스템입니다.

## 📋 주요 기능

- ✅ 실시간 센서 데이터 수집 및 저장
- ✅ 위험도 자동 계산 (0: 정상, 1: 주의, 2: 위험)
- ✅ WebSocket 기반 실시간 대시보드
- ✅ 센서 데이터 이력 조회 및 CSV 다운로드
- ✅ 임계값 설정 UI
- ✅ 반응형 웹 디자인

## 🛠️ 기술 스택

- **Backend**: FastAPI, SQLAlchemy, WebSocket
- **Database**: MariaDB (MySQL)
- **Frontend**: Jinja2, Chart.js, Vanilla JavaScript
- **Server**: Uvicorn

## 📦 설치 방법

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. MariaDB 설정

MariaDB가 설치되어 있어야 합니다. 데이터베이스를 생성하세요:

```sql
CREATE DATABASE sinker_iot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 데이터베이스 연결 설정

`app/config.py` 파일에서 DB 연결 정보를 확인하세요:

```python
DB_URL = "mysql+pymysql://root:1234@localhost:3306/sinker_iot"
```

필요시 사용자명, 비밀번호, 호스트를 수정하세요.

## 🚀 실행 방법

### 개발 환경

프로젝트 루트 디렉토리에서 다음 명령어를 실행하세요:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 배포 환경

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 접속 방법

서버 실행 후 브라우저에서 다음 주소로 접속:

- **실시간 대시보드**: http://localhost:8000/
- **이력 조회**: http://localhost:8000/history
- **임계값 설정**: http://localhost:8000/config
- **API 문서**: http://localhost:8000/docs

## 📡 센서 데이터 전송 방법

라즈베리파이 또는 다른 센서에서 다음과 같은 형식으로 데이터를 전송하세요:

### POST /sensor

```json
{
  "moisture": 450.5,
  "accel": {
    "x": 0.05,
    "y": -0.03,
    "z": 9.80
  },
  "gyro": {
    "x": 0.02,
    "y": -0.01,
    "z": 0.00
  },
  "vibration_raw": 3.2,
  "timestamp": "2025-11-19T12:30:05"
}
```

### Python 예시 코드

```python
import requests
import json
from datetime import datetime

url = "http://localhost:8000/sensor"
data = {
    "moisture": 450.5,
    "accel": {"x": 0.05, "y": -0.03, "z": 9.80},
    "gyro": {"x": 0.02, "y": -0.01, "z": 0.00},
    "vibration_raw": 3.2,
    "timestamp": datetime.now().isoformat()
}

response = requests.post(url, json=data)
print(response.json())
```

## 📊 API 엔드포인트

### 센서 데이터

- `POST /sensor` - 센서 데이터 수신
- `GET /latest` - 최신 센서 데이터 1건 조회
- `GET /history` - 센서 데이터 이력 조회
  - 쿼리 파라미터: `minutes`, `start`, `end`
- `GET /history/csv` - CSV 파일 다운로드

### 임계값 관리

- `GET /config/api/thresholds` - 임계값 목록 조회
- `POST /config/api/thresholds` - 임계값 업데이트

### WebSocket

- `WS /ws` - 실시간 데이터 스트리밍

## 🎯 위험도 계산 로직

시스템은 다음 4가지 요소를 기반으로 위험도를 계산합니다:

1. **토양 수분**: 설정된 임계값 초과 여부
2. **진동 센서**: 설정된 임계값 초과 여부
3. **가속도 변화량**: 직전 값 대비 X/Y/Z 축 변화량
4. **자이로 변화량**: 직전 값 대비 X/Y/Z 축 변화량

최종 위험도는 위 4가지 중 **가장 높은 값**으로 결정됩니다.

## 📁 프로젝트 구조

```
app/
├── __init__.py          # 패키지 초기화
├── main.py              # FastAPI 메인 애플리케이션
├── config.py            # 설정 파일 (DB, 임계값)
├── database.py          # 데이터베이스 연결
├── models.py            # SQLAlchemy ORM 모델
├── schemas.py           # Pydantic 스키마
├── crud.py              # 비즈니스 로직
├── websocket_manager.py # WebSocket 관리
├── templates/           # Jinja2 템플릿
│   ├── index.html       # 실시간 대시보드
│   ├── history.html     # 이력 조회
│   └── config.html      # 임계값 설정
└── static/              # 정적 파일
    ├── css/
    │   └── style.css
    └── js/
        ├── dashboard.js
        ├── history.js
        └── config.js
```

## 🔧 임계값 설정

기본 임계값은 `app/config.py`에 정의되어 있습니다:

```python
DEFAULT_THRESHOLDS = {
    "moisture_warning": 600.0,      # 토양 수분 주의
    "moisture_danger": 700.0,       # 토양 수분 위험
    "vibration_warning": 1.0,       # 진동 주의
    "vibration_danger": 2.0,        # 진동 위험
    "accel_delta_warning": 1.0,     # 가속도 변화 주의
    "accel_delta_danger": 2.0,      # 가속도 변화 위험
    "gyro_delta_warning": 5.0,      # 자이로 변화 주의
    "gyro_delta_danger": 10.0       # 자이로 변화 위험
}
```

웹 UI에서 실시간으로 수정 가능합니다.

## 🐛 트러블슈팅

### MariaDB 연결 오류

```bash
# MariaDB 서비스 확인
sudo systemctl status mariadb

# MariaDB 시작
sudo systemctl start mariadb
```

### 포트 충돌

다른 포트를 사용하려면:

```bash
uvicorn app.main:app --reload --port 8080
```

### 테이블 생성 오류

서버는 시작 시 자동으로 테이블을 생성합니다. 
수동으로 테이블을 생성하려면 Python 콘솔에서:

```python
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
```

## 📝 라이선스

MIT License

## 👥 기여

이슈와 풀 리퀘스트를 환영합니다!

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
