# 🚀 맥북-라즈베리파이 핫스팟 연결 가이드

## 📱 1. 맥북 핫스팟 IP 주소 확인

### 방법 1: 시스템 환경설정
1. **시스템 환경설정** > **네트워크** 클릭
2. 좌측에서 활성화된 연결 선택 (Wi-Fi 또는 개인용 핫스팟)
3. IP 주소 확인 (예: `192.168.2.1`)

### 방법 2: 터미널
```bash
ifconfig | grep "inet "
```

출력 예시:
```
inet 192.168.2.1 netmask 0xffffff00 broadcast 192.168.2.255
```
→ `192.168.2.1`이 맥북의 IP 주소입니다.

---

## 🔧 2. 라즈베리파이 설정 수정

### config.py 파일 수정
라즈베리파이에서 `/home/pi/Sinker_IOT/raspberry_pi/config.py` 파일을 열고:

```python
# 맥북의 IP 주소로 변경 (위에서 확인한 주소 사용)
SERVER_URL = "http://192.168.2.1:8000/sensor"
```

---

## 🖥️ 3. 맥북에서 서버 실행

### 터미널에서 프로젝트 폴더로 이동
```bash
cd ~/Sinker_IOT
```

### 가상환경 활성화 (있는 경우)
```bash
source venv/bin/activate  # 가상환경 이름에 맞게 수정
```

### 의존성 설치 (최초 1회)
```bash
pip install -r requirements.txt
```

### FastAPI 서버 실행
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**중요**: `--host 0.0.0.0` 옵션을 반드시 사용해야 외부(라즈베리파이)에서 접속 가능합니다!

서버가 정상 실행되면:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## 🍓 4. 라즈베리파이에서 센서 클라이언트 실행

### SSH로 라즈베리파이 접속
```bash
ssh pi@<라즈베리파이_IP>
```

### 프로젝트 폴더로 이동
```bash
cd ~/Sinker_IOT/raspberry_pi
```

### 센서 테스트 (로컬 확인)
```bash
python3 sensor_test.py
```
- 센서 값이 정상적으로 출력되는지 확인
- Ctrl+C로 종료

### 서버로 데이터 전송 시작
```bash
python3 sensor_client.py
```

정상 동작 시 출력:
```
✅ [1] 전송 성공 - 위험도: 0
✅ [2] 전송 성공 - 위험도: 0
...
```

---

## 🌐 5. 웹 대시보드 접속

### 맥북에서 접속
브라우저 주소창에 입력:
```
http://localhost:8000
```

### 같은 네트워크의 다른 기기에서 접속
```
http://<맥북_IP>:8000
```
예: `http://192.168.2.1:8000`

---

## 🔍 6. 연결 확인 방법

### 라즈베리파이에서 맥북 핑 테스트
```bash
ping 192.168.2.1
```

성공 시:
```
64 bytes from 192.168.2.1: icmp_seq=1 ttl=64 time=1.234 ms
```

### 서버 연결 테스트
```bash
curl http://192.168.2.1:8000/health
```

성공 시:
```json
{"status":"healthy","service":"sinkhole-warning-system"}
```

---

## ⚠️ 문제 해결

### 연결 실패 시
1. **맥북 방화벽 확인**
   - 시스템 환경설정 > 보안 및 개인 정보 보호 > 방화벽
   - 방화벽이 켜져 있으면 Python 또는 uvicorn 허용 추가

2. **핫스팟 재시작**
   - 맥북 핫스팟을 껐다가 다시 켜기
   - 라즈베리파이 Wi-Fi 재연결

3. **IP 주소 재확인**
   - 핫스팟 재시작 시 IP가 변경될 수 있음
   - `ifconfig` 명령어로 다시 확인

4. **포트 사용 확인**
   ```bash
   lsof -i :8000
   ```
   - 다른 프로그램이 8000번 포트를 사용 중인지 확인

---

## 📝 전체 실행 순서 요약

1. 맥북 IP 확인: `ifconfig`
2. 라즈베리파이 `config.py` 수정
3. 맥북에서 서버 실행: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
4. 라즈베리파이에서 클라이언트 실행: `python3 sensor_client.py`
5. 브라우저에서 대시보드 접속: `http://localhost:8000`

---

## 🎯 빠른 시작 명령어

### 맥북
```bash
cd ~/Sinker_IOT
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 라즈베리파이
```bash
cd ~/Sinker_IOT/raspberry_pi
python3 sensor_client.py
```

완료! 🎉
