# 📦 라즈베리파이 센서 시스템 - 리팩토링 완료

## 🎯 프로젝트 개요
동료의 **정상 작동 코드 기준**으로 전체 시스템을 깔끔하게 리팩토링했습니다.

---

## 📁 파일 구조

```
Sinker_IOT/
├── app/                          # FastAPI 서버 (맥북에서 실행)
│   ├── main.py                   # 메인 서버
│   ├── database.py
│   ├── models.py
│   └── ...
│
├── raspberry_pi/                 # 라즈베리파이 코드
│   ├── config.py                 # ⚙️ 설정 파일 (IP 주소 수정 필요)
│   ├── sensor_manager.py         # 🔧 센서 통합 관리
│   ├── sensor_test.py            # 🧪 로컬 테스트 (센서만)
│   ├── sensor_client.py          # 📡 서버 전송 클라이언트
│   ├── requirements.txt          # 📦 필수 패키지
│   ├── HOTSPOT_GUIDE.md          # 📱 핫스팟 연결 가이드
│   └── README_REFACTORED.md      # 📖 이 문서
│
└── requirements.txt              # 서버용 패키지
```

---

## 🔌 하드웨어 구성 (동료 코드 기준)

### 1️⃣ 진동 센서 (SW-420)
- **연결**: GPIO17 (BCM)
- **타입**: Digital Output
- **용도**: 움직임/진동 감지

### 2️⃣ 토양 수분 센서 (MCP3008)
- **연결**: SPI (Bus0, Device0)
- **채널**: CH0
- **타입**: Analog (0~1023)
- **용도**: 토양 수분 측정

### 3️⃣ 기울기/가속도 센서 (MPU6050)
- **연결**: I2C
- **주소**: 0x68
- **용도**: 가속도, 자이로스코프 데이터

---

## 🚀 사용 방법

### 1단계: 맥북 IP 주소 확인
```bash
ifconfig | grep "inet "
```
예: `192.168.2.1`

### 2단계: config.py 수정
라즈베리파이의 `raspberry_pi/config.py` 파일에서:
```python
SERVER_URL = "http://192.168.2.1:8000/sensor"  # 맥북 IP로 변경
```

### 3단계: 맥북에서 서버 실행
```bash
cd ~/Sinker_IOT
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4단계: 라즈베리파이 패키지 설치 (최초 1회)
```bash
cd ~/Sinker_IOT/raspberry_pi
pip3 install -r requirements.txt
```

### 5단계: 센서 테스트
```bash
python3 sensor_test.py
```
- 센서 값이 1초마다 출력됩니다
- 진동 감지 시 즉시 경고 메시지 출력
- Ctrl+C로 종료

### 6단계: 서버로 전송 시작
```bash
python3 sensor_client.py
```
- 1초마다 서버로 데이터 전송
- 전송 성공/실패 로그 출력
- Ctrl+C로 종료

---

## 📊 각 파일 설명

### 📄 config.py
```python
SERVER_URL = "http://192.168.2.1:8000/sensor"  # 맥북 IP
SEND_INTERVAL = 1                               # 전송 간격 (초)
VIBRATION_PIN = 17                              # GPIO 핀
MOISTURE_CHANNEL = 0                            # MCP3008 채널
MPU6050_ADDRESS = 0x68                          # I2C 주소
```

### 🔧 sensor_manager.py
센서 통합 관리 클래스
```python
manager = SensorManager()
data = manager.read_all()  # 모든 센서 한 번에 읽기
manager.cleanup()          # 종료 시 정리
```

### 🧪 sensor_test.py
로컬 테스트용 - 센서 값만 출력
- 서버 연결 없이 동작
- 1초마다 모든 센서 값 출력
- 진동 감지 시 이벤트 콜백

### 📡 sensor_client.py
서버 전송 클라이언트
- 1초마다 센서 데이터 수집
- 서버로 POST 전송
- 재시도 로직 포함 (최대 3회)
- 통계 출력

---

## 🔄 데이터 흐름

```
[라즈베리파이]
    ↓
sensor_manager.py (센서 읽기)
    ↓
sensor_client.py (데이터 수집)
    ↓
requests.post() (HTTP 전송)
    ↓
[맥북 핫스팟 네트워크]
    ↓
FastAPI 서버 (app/main.py)
    ↓
데이터베이스 저장 + WebSocket 브로드캐스트
    ↓
웹 대시보드 (http://맥북IP:8000)
```

---

## ✅ 주요 개선 사항

### 1. 동료 코드 구조 100% 반영
- GPIO17 진동 센서
- SPI MCP3008 토양 수분
- I2C MPU6050 가속도/자이로

### 2. 깔끔한 모듈 분리
- `sensor_manager.py`: 센서 통합
- `sensor_test.py`: 로컬 테스트
- `sensor_client.py`: 서버 전송
- `config.py`: 설정 통합

### 3. 에러 처리 강화
- 재시도 로직 (최대 3회)
- 타임아웃 설정
- 연결 실패 시 계속 재시도

### 4. 명확한 로그 출력
```
✅ [1] 전송 성공 - 위험도: 0
📡 수분: 512 | 진동: 0 | 가속도 Z: 9.81
🚨 [즉시 경고] 진동이 감지되었습니다!
```

---

## 🐛 문제 해결

### 센서가 작동하지 않을 때
```bash
# GPIO 권한 확인
sudo usermod -a -G gpio $USER

# I2C 활성화 확인
sudo raspi-config
# Interface Options > I2C > Enable

# SPI 활성화 확인
sudo raspi-config
# Interface Options > SPI > Enable

# 재부팅
sudo reboot
```

### 서버 연결 실패 시
1. 맥북 서버가 실행 중인지 확인
2. 맥북 방화벽 설정 확인
3. IP 주소가 맞는지 재확인
4. 핑 테스트: `ping 192.168.2.1`

### 패키지 설치 오류 시
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip
sudo apt-get install i2c-tools python3-smbus

pip3 install --upgrade pip
pip3 install -r requirements.txt
```

---

## 📱 핫스팟 연결 상세 가이드

자세한 내용은 **`HOTSPOT_GUIDE.md`** 파일을 참고하세요!

---

## 🎉 완료!

이제 다음 명령어만으로 전체 시스템이 작동합니다:

**맥북:**
```bash
cd ~/Sinker_IOT
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**라즈베리파이:**
```bash
cd ~/Sinker_IOT/raspberry_pi
python3 sensor_client.py
```

**브라우저:**
```
http://localhost:8000  (맥북에서)
http://192.168.2.1:8000  (다른 기기에서)
```

---

## 📞 추가 도움

문제가 발생하면:
1. `sensor_test.py`로 센서 단독 테스트
2. `config.py`의 IP 주소 재확인
3. 맥북 서버 로그 확인
4. 라즈베리파이 연결 상태 확인

**모든 코드는 동료의 정상 작동 코드를 기반으로 작성되었습니다!** ✨
