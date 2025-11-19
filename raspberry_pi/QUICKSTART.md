# 🍓 라즈베리파이 센서 시스템 빠른 시작

## ⚡ 5분 안에 시작하기

### 1단계: 파일 복사 (1분)

라즈베리파이에 이 폴더 전체를 복사하세요:

```bash
# 방법 1: Git 클론
cd ~
git clone <저장소_URL> Sinker_IOT
cd Sinker_IOT/raspberry_pi

# 방법 2: SCP로 복사 (다른 컴퓨터에서)
scp -r raspberry_pi/ pi@raspberrypi.local:~/Sinker_IOT/
```

### 2단계: 패키지 설치 (2분)

```bash
cd ~/Sinker_IOT/raspberry_pi
pip3 install -r requirements.txt
```

### 3단계: 설정 수정 (1분)

`config.py` 파일을 열어 서버 주소 수정:

```bash
nano config.py
```

```python
SERVER_URL = "http://YOUR_SERVER_IP:8000/sensor"
```

저장: `Ctrl+X` → `Y` → `Enter`

### 4단계: 센서 테스트 (1분)

```bash
python3 sensor_status.py
python3 sensor_test.py
```

### 5단계: 실행! (즉시)

```bash
python3 sensor_client.py
```

---

## 🔌 하드웨어 연결 (한눈에 보기)

### MPU6050 (가속도 + 자이로)
```
MPU6050    →    라즈베리파이
VCC        →    3.3V (Pin 1)
GND        →    GND (Pin 6)
SDA        →    GPIO 2 (Pin 3)
SCL        →    GPIO 3 (Pin 5)
```

### ADS1115 (ADC)
```
ADS1115    →    라즈베리파이
VDD        →    3.3V (Pin 1)
GND        →    GND (Pin 6)
SDA        →    GPIO 2 (Pin 3)
SCL        →    GPIO 3 (Pin 5)
```

### 센서들
```
토양 수분 센서 OUT  →  ADS1115 A0
진동 센서 OUT      →  ADS1115 A1
```

---

## 📋 체크리스트

### 하드웨어
- [ ] 라즈베리파이 전원 연결
- [ ] MPU6050 I2C 연결
- [ ] ADS1115 I2C 연결
- [ ] 토양 수분 센서 연결
- [ ] 진동 센서 연결

### 소프트웨어
- [ ] I2C 활성화 (`sudo raspi-config`)
- [ ] Python 패키지 설치
- [ ] config.py 서버 주소 설정
- [ ] 센서 연결 확인 (`sensor_status.py`)

### 테스트
- [ ] I2C 장치 스캔 (`sudo i2cdetect -y 1`)
- [ ] 센서 읽기 테스트 (`sensor_test.py`)
- [ ] 서버 통신 테스트 (센서 클라이언트 실행)

---

## 🚀 자동 실행 설정

### systemd 서비스 등록

```bash
# 1. 서비스 파일 복사
sudo cp sinkhole-sensor.service /etc/systemd/system/

# 2. 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable sinkhole-sensor.service

# 3. 서비스 시작
sudo systemctl start sinkhole-sensor.service

# 4. 상태 확인
sudo systemctl status sinkhole-sensor.service
```

이제 라즈베리파이가 부팅될 때마다 자동으로 센서 클라이언트가 실행됩니다!

---

## 📊 명령어 모음

### 센서 관련
```bash
# 센서 상태 확인
python3 sensor_status.py

# 센서 테스트
python3 sensor_test.py

# 센서 클라이언트 실행
python3 sensor_client.py

# 토양 수분 캘리브레이션
python3 calibrate_moisture.py

# 진동 센서 캘리브레이션
python3 calibrate_vibration.py
```

### I2C 관련
```bash
# I2C 장치 스캔
sudo i2cdetect -y 1

# I2C 활성화
sudo raspi-config
# → Interface Options → I2C → Yes
```

### 서비스 관련
```bash
# 서비스 시작
sudo systemctl start sinkhole-sensor.service

# 서비스 중지
sudo systemctl stop sinkhole-sensor.service

# 서비스 재시작
sudo systemctl restart sinkhole-sensor.service

# 서비스 상태
sudo systemctl status sinkhole-sensor.service

# 로그 보기
sudo journalctl -u sinkhole-sensor.service -f
```

### 백그라운드 실행
```bash
# nohup으로 실행
nohup python3 sensor_client.py > sensor.log 2>&1 &

# 프로세스 확인
ps aux | grep sensor_client

# 종료
pkill -f sensor_client.py
```

---

## 🐛 문제 해결

### I2C 장치가 안 보여요
```bash
# I2C 활성화 확인
sudo raspi-config
# → Interface Options → I2C

# 재부팅
sudo reboot

# I2C 스캔
sudo i2cdetect -y 1
```

### 센서 값이 이상해요
```bash
# 캘리브레이션 실행
python3 calibrate_moisture.py
python3 calibrate_vibration.py
```

### 서버에 연결이 안 돼요
```bash
# 네트워크 확인
ping YOUR_SERVER_IP

# config.py 확인
nano config.py

# 서버 상태 확인 (서버 컴퓨터에서)
curl http://localhost:8000/health
```

### 패키지 설치 오류
```bash
# pip 업그레이드
pip3 install --upgrade pip

# 패키지 재설치
pip3 install -r requirements.txt --force-reinstall
```

---

## 📱 실시간 모니터링

센서가 정상 작동하면:

1. **대시보드 접속**: http://SERVER_IP:8000/
2. **실시간 그래프** 확인
3. **위험도 배지** 모니터링

---

## 💡 팁

### 전력 절약
```python
# config.py에서 전송 간격 늘리기
SEND_INTERVAL = 10  # 3초 → 10초
```

### 로그 관리
```bash
# 오래된 로그 삭제
find . -name "*.log" -mtime +7 -delete
```

### 원격 접속
```bash
# SSH 활성화
sudo raspi-config
# → Interface Options → SSH

# 접속
ssh pi@raspberrypi.local
```

---

## 🎉 완료!

이제 라즈베리파이가 자동으로 센서 데이터를 수집하고 서버에 전송합니다!

문제가 있으면 `README.md`를 참고하세요.
