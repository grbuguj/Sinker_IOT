# 라즈베리파이 센서 시스템 설정 가이드

## 📋 준비물

### 하드웨어
- 🍓 **라즈베리파이** (3/4/5 권장)
- 💧 **토양 수분 센서** (아날로그 출력)
  - 예: Capacitive Soil Moisture Sensor v1.2
- 📳 **진동 센서**
  - 예: SW-420 진동 센서 또는 아날로그 진동 센서
- 📐 **MPU6050** (가속도계 + 자이로스코프)
  - I2C 통신
- 🔌 **ADC 컨버터** (아날로그 센서용)
  - 예: ADS1115 (16-bit, 4채널)
  - 또는 MCP3008 (10-bit, 8채널)
- 🔗 **점퍼 케이블 및 브레드보드**

### 소프트웨어
- Raspberry Pi OS (Bullseye 이상)
- Python 3.7+
- I2C 활성화
- 인터넷 연결

---

## 🔧 1. 라즈베리파이 초기 설정

### 1.1 시스템 업데이트
```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 I2C 활성화
```bash
sudo raspi-config
```
- `3 Interface Options` → `I5 I2C` → `Yes` 선택
- 재부팅: `sudo reboot`

### 1.3 필요한 시스템 패키지 설치
```bash
sudo apt install -y python3-pip python3-smbus i2c-tools git
```

### 1.4 I2C 장치 확인
```bash
sudo i2cdetect -y 1
```
MPU6050이 연결되면 `0x68` 또는 `0x69` 주소가 보입니다.

---

## 🔌 2. 하드웨어 연결

### 2.1 MPU6050 연결 (I2C)
```
MPU6050          라즈베리파이
VCC      →      3.3V (Pin 1)
GND      →      GND (Pin 6)
SDA      →      GPIO 2 (SDA, Pin 3)
SCL      →      GPIO 3 (SCL, Pin 5)
```

### 2.2 ADS1115 연결 (I2C + 아날로그 센서)
```
ADS1115          라즈베리파이
VDD      →      3.3V (Pin 1)
GND      →      GND (Pin 6)
SDA      →      GPIO 2 (SDA, Pin 3)
SCL      →      GPIO 3 (SCL, Pin 5)

A0       →      토양 수분 센서 출력
A1       →      진동 센서 출력
A2       →      (예비)
A3       →      (예비)
```

### 2.3 센서 전원 연결
```
토양 수분 센서
VCC      →      3.3V
GND      →      GND
AOUT     →      ADS1115 A0

진동 센서
VCC      →      3.3V
GND      →      GND
AOUT     →      ADS1115 A1
```

---

## 📦 3. Python 패키지 설치

### 3.1 requirements.txt 설치
```bash
cd raspberry_pi
pip3 install -r requirements.txt
```

### 3.2 개별 설치 (선택사항)
```bash
pip3 install requests adafruit-circuitpython-ads1x15 smbus2 mpu6050-raspberrypi
```

---

## ⚙️ 4. 설정 파일 수정

`config.py` 파일을 열어 서버 주소 수정:

```python
# 서버가 같은 네트워크의 다른 컴퓨터에 있는 경우
SERVER_URL = "http://192.168.1.100:8000/sensor"

# 서버가 클라우드에 있는 경우
SERVER_URL = "http://your-domain.com:8000/sensor"
```

---

## 🚀 5. 실행 방법

### 5.1 테스트 모드 (센서 읽기만)
```bash
python3 sensor_test.py
```

### 5.2 실제 데이터 전송
```bash
python3 sensor_client.py
```

### 5.3 백그라운드 실행
```bash
nohup python3 sensor_client.py > sensor.log 2>&1 &
```

### 5.4 부팅 시 자동 실행

#### systemd 서비스 생성
```bash
sudo nano /etc/systemd/system/sinkhole-sensor.service
```

내용:
```ini
[Unit]
Description=Sinkhole Sensor Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Sinker_IOT/raspberry_pi
ExecStart=/usr/bin/python3 /home/pi/Sinker_IOT/raspberry_pi/sensor_client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 서비스 활성화
```bash
sudo systemctl daemon-reload
sudo systemctl enable sinkhole-sensor.service
sudo systemctl start sinkhole-sensor.service
```

#### 상태 확인
```bash
sudo systemctl status sinkhole-sensor.service
```

#### 로그 확인
```bash
sudo journalctl -u sinkhole-sensor.service -f
```

---

## 🔍 6. 센서 캘리브레이션

### 6.1 토양 수분 센서
```bash
python3 calibrate_moisture.py
```

1. 센서를 **건조한 공기**에 노출 → 최솟값 기록
2. 센서를 **물에 담금** → 최댓값 기록
3. `config.py`에 값 입력

### 6.2 진동 센서
```bash
python3 calibrate_vibration.py
```

1. 센서를 **정지 상태**로 둠 → 기준값 기록
2. 가벼운 진동 → 임계값 설정
3. `config.py`에 값 입력

---

## 🐛 7. 문제 해결

### I2C 장치가 안 보일 때
```bash
# I2C 활성화 확인
sudo raspi-config

# I2C 장치 스캔
sudo i2cdetect -y 1

# 권한 확인
sudo usermod -a -G i2c pi
```

### MPU6050 읽기 오류
```python
# I2C 주소 변경 시도
mpu = mpu6050(0x69)  # 기본값은 0x68
```

### 센서 값이 이상할 때
```bash
# 센서 테스트 모드 실행
python3 sensor_test.py

# 연결 상태 확인
sudo i2cdetect -y 1
```

### 서버 연결 실패
```bash
# 네트워크 확인
ping SERVER_IP

# 포트 확인
telnet SERVER_IP 8000
```

---

## 📊 8. 모니터링

### 실시간 로그 확인
```bash
tail -f sensor.log
```

### 센서 상태 확인
```bash
python3 sensor_status.py
```

---

## 🔒 9. 보안 권장사항

1. **SSH 비밀번호 변경**
   ```bash
   passwd
   ```

2. **방화벽 설정**
   ```bash
   sudo apt install ufw
   sudo ufw allow 22
   sudo ufw enable
   ```

3. **자동 업데이트 설정**
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

---

## 📝 10. 유지보수

### 로그 정리
```bash
# 오래된 로그 삭제
find /home/pi/Sinker_IOT/raspberry_pi -name "*.log" -mtime +7 -delete
```

### 시스템 모니터링
```bash
# CPU 온도
vcgencmd measure_temp

# 메모리 사용량
free -h

# 디스크 사용량
df -h
```

---

## 🎯 다음 단계

1. ✅ 하드웨어 연결
2. ✅ Python 패키지 설치
3. ✅ config.py 수정 (서버 주소)
4. ✅ 센서 테스트 (`sensor_test.py`)
5. ✅ 캘리브레이션
6. ✅ 데이터 전송 시작 (`sensor_client.py`)
7. ✅ 서비스 등록 (부팅 시 자동 실행)

---

## 📞 지원

문제가 발생하면:
1. `sensor_test.py`로 센서 상태 확인
2. `sudo journalctl -u sinkhole-sensor.service -f`로 로그 확인
3. 서버의 `/docs`에서 API 테스트

---

**준비 완료!** 🎉

이제 라즈베리파이가 자동으로 센서 데이터를 수집하고 서버에 전송합니다!
