# 🍓 라즈베리파이 센서 시스템 - 완전 가이드

## 📦 생성된 파일 목록

```
raspberry_pi/
├── 📄 README.md                    # 상세 설치 및 설정 가이드
├── 📄 QUICKSTART.md                # 5분 빠른 시작 가이드
├── 📄 WIRING.md                    # 하드웨어 연결 다이어그램
├── 📄 requirements.txt             # Python 패키지 목록
├── ⚙️ config.py                    # 설정 파일
├── 🔧 sensor_manager.py            # 센서 매니저 (핵심)
├── 🚀 sensor_client.py             # 메인 클라이언트 (데이터 전송)
├── 🧪 sensor_test.py               # 센서 테스트 도구
├── 📊 sensor_status.py             # 시스템 진단 도구
├── 🎯 calibrate_moisture.py        # 토양 수분 캘리브레이션
├── 🎯 calibrate_vibration.py       # 진동 센서 캘리브레이션
└── 🔧 sinkhole-sensor.service      # systemd 서비스 파일
```

---

## 🎯 핵심 기능

### ✅ 센서 데이터 수집
- **MPU6050**: 3축 가속도 + 3축 자이로스코프
- **토양 수분 센서**: 아날로그 출력 (캘리브레이션 가능)
- **진동 센서**: 아날로그 출력 (캘리브레이션 가능)

### ✅ 데이터 처리
- 이동 평균 필터링 (노이즈 제거)
- 자동 스케일링 및 정규화
- 실시간 데이터 검증

### ✅ 서버 통신
- HTTP POST로 데이터 전송
- 자동 재시도 (최대 3회)
- 연결 타임아웃 처리
- 로그 기록 (파일 회전)

### ✅ 자동 실행
- systemd 서비스 지원
- 부팅 시 자동 시작
- 오류 시 자동 재시작
- 원격 관리 가능

---

## 🚀 단계별 설치 가이드

### 1️⃣ 하드웨어 준비 (10분)

**필요한 부품:**
- 라즈베리파이 (3/4/5)
- MPU6050 모듈
- ADS1115 모듈
- 토양 수분 센서 (Capacitive)
- 진동 센서 (SW-420 또는 아날로그)
- 점퍼 케이블 및 브레드보드

**연결 방법:**
→ `WIRING.md` 참고

### 2️⃣ 라즈베리파이 설정 (5분)

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# I2C 활성화
sudo raspi-config
# → Interface Options → I2C → Yes

# 재부팅
sudo reboot

# I2C 도구 설치
sudo apt install -y python3-pip i2c-tools
```

### 3️⃣ 파일 복사 (2분)

```bash
# Git 클론
cd ~
git clone <저장소_URL> Sinker_IOT
cd Sinker_IOT/raspberry_pi

# 또는 SCP로 복사
scp -r raspberry_pi/ pi@raspberrypi.local:~/Sinker_IOT/
```

### 4️⃣ Python 패키지 설치 (3분)

```bash
cd ~/Sinker_IOT/raspberry_pi
pip3 install -r requirements.txt
```

### 5️⃣ 설정 수정 (1분)

```bash
nano config.py
```

**수정할 항목:**
```python
# 서버 URL (필수!)
SERVER_URL = "http://YOUR_SERVER_IP:8000/sensor"

# 전송 간격 (선택)
SEND_INTERVAL = 3  # 초
```

### 6️⃣ 센서 확인 (2분)

```bash
# I2C 장치 스캔
sudo i2cdetect -y 1

# 시스템 진단
python3 sensor_status.py

# 센서 테스트
python3 sensor_test.py
```

### 7️⃣ 캘리브레이션 (5분)

```bash
# 토양 수분 센서
python3 calibrate_moisture.py

# 진동 센서
python3 calibrate_vibration.py
```

### 8️⃣ 실행 테스트 (1분)

```bash
python3 sensor_client.py
```

Ctrl+C로 중지

### 9️⃣ 자동 실행 설정 (2분)

```bash
# 서비스 파일 복사
sudo cp sinkhole-sensor.service /etc/systemd/system/

# 경로 수정 (필요시)
sudo nano /etc/systemd/system/sinkhole-sensor.service

# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable sinkhole-sensor.service
sudo systemctl start sinkhole-sensor.service

# 상태 확인
sudo systemctl status sinkhole-sensor.service
```

---

## 📋 일일 운영 가이드

### 시작
```bash
sudo systemctl start sinkhole-sensor.service
```

### 중지
```bash
sudo systemctl stop sinkhole-sensor.service
```

### 재시작
```bash
sudo systemctl restart sinkhole-sensor.service
```

### 상태 확인
```bash
sudo systemctl status sinkhole-sensor.service
```

### 로그 확인
```bash
# 실시간 로그
sudo journalctl -u sinkhole-sensor.service -f

# 최근 100줄
sudo journalctl -u sinkhole-sensor.service -n 100

# 파일 로그
tail -f sensor.log
```

---

## 🔍 문제 해결

### 센서가 인식 안 됨

**증상**: `i2cdetect`에서 장치가 안 보임

**해결**:
```bash
# I2C 활성화 확인
sudo raspi-config

# 재부팅
sudo reboot

# 연결 상태 확인
sudo i2cdetect -y 1
```

### 센서 값이 이상함

**증상**: 값이 튀거나 0만 나옴

**해결**:
```bash
# 캘리브레이션 다시 실행
python3 calibrate_moisture.py
python3 calibrate_vibration.py

# config.py에 값 적용
nano config.py
```

### 서버 연결 안 됨

**증상**: 전송 실패 메시지

**해결**:
```bash
# 네트워크 확인
ping YOUR_SERVER_IP

# 서버 상태 확인
curl http://YOUR_SERVER_IP:8000/health

# config.py 확인
nano config.py
```

### 서비스가 계속 재시작됨

**증상**: `systemctl status`에서 재시작 반복

**해결**:
```bash
# 로그 확인
sudo journalctl -u sinkhole-sensor.service -n 50

# 수동 실행으로 에러 확인
cd ~/Sinker_IOT/raspberry_pi
python3 sensor_client.py
```

---

## 📊 모니터링

### 실시간 데이터 확인

**방법 1: 로그**
```bash
tail -f sensor.log
```

**방법 2: 웹 대시보드**
- 브라우저: `http://SERVER_IP:8000/`

### 센서 상태 확인
```bash
python3 sensor_status.py
```

### 통계 확인
```bash
# 로그에서 통계 추출
grep "통계" sensor.log -A 5
```

---

## 🔧 고급 설정

### 전송 간격 변경
```python
# config.py
SEND_INTERVAL = 10  # 3초 → 10초
```

### 필터 조정
```python
# config.py
MOVING_AVERAGE_WINDOW = 10  # 5 → 10 (더 부드러운 값)
```

### 재시도 설정
```python
# config.py
MAX_RETRIES = 5  # 3 → 5 (더 많은 재시도)
RETRY_DELAY = 10  # 5 → 10 (더 긴 대기)
```

### 로그 레벨 변경
```python
# config.py
LOG_LEVEL = "DEBUG"  # 더 상세한 로그
```

---

## 🎓 코드 이해하기

### sensor_manager.py
- **역할**: 모든 센서 읽기 통합
- **핵심 메서드**:
  - `read_moisture()`: 토양 수분
  - `read_vibration()`: 진동
  - `read_accel()`: 가속도
  - `read_gyro()`: 자이로
  - `read_all()`: 모든 센서 한 번에

### sensor_client.py
- **역할**: 데이터 수집 및 서버 전송
- **핵심 기능**:
  - 주기적 데이터 수집
  - HTTP POST 전송
  - 재시도 로직
  - 로그 기록
  - 시그널 핸들링

### config.py
- **역할**: 모든 설정값 중앙 관리
- **수정 가능 항목**:
  - 서버 URL
  - 전송 간격
  - I2C 주소
  - 캘리브레이션 값
  - 필터 설정

---

## 🌟 Best Practices

### 전력 관리
- 불필요한 USB 장치 제거
- 화면 끄기: `sudo vcgencmd display_power 0`
- 전송 간격 조정으로 CPU 사용률 감소

### 데이터 품질
- 정기적 캘리브레이션 (월 1회)
- 센서 청소 (토양 수분 센서)
- 연결 상태 점검

### 유지보수
- 로그 정기 정리
- 시스템 업데이트
- 백업 (config.py, 캘리브레이션 값)

---

## 📞 지원

### 진단 도구 실행
```bash
python3 sensor_status.py
```

### 로그 수집
```bash
# 시스템 로그
sudo journalctl -u sinkhole-sensor.service > system.log

# 애플리케이션 로그
cp sensor.log app.log
```

### 이슈 보고 시 포함 정보
1. `sensor_status.py` 출력
2. `i2cdetect -y 1` 출력
3. 로그 파일 (최근 100줄)
4. 연결 사진

---

## 🎉 완료!

라즈베리파이 센서 시스템이 완전히 준비되었습니다!

**다음 단계:**
1. ✅ 하드웨어 연결 확인
2. ✅ 센서 테스트
3. ✅ 서버 통신 확인
4. ✅ 자동 실행 설정
5. ✅ 웹 대시보드에서 실시간 모니터링

**문제가 있나요?**
- `README.md`: 상세 가이드
- `QUICKSTART.md`: 빠른 시작
- `WIRING.md`: 연결 다이어그램

**Happy Monitoring!** 🎊
