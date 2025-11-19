"""
테스트용 센서 데이터 전송 스크립트
랜덤 센서 데이터를 서버에 전송합니다.
"""

import requests
import random
import time
from datetime import datetime

# 서버 URL
SERVER_URL = "http://localhost:8000/sensor"

def generate_sensor_data():
    """
    랜덤 센서 데이터 생성
    """
    # 기본값 + 랜덤 변동
    moisture = 450 + random.uniform(-50, 150)
    
    accel_x = random.uniform(-0.1, 0.1)
    accel_y = random.uniform(-0.1, 0.1)
    accel_z = 9.8 + random.uniform(-0.2, 0.2)
    
    gyro_x = random.uniform(-0.05, 0.05)
    gyro_y = random.uniform(-0.05, 0.05)
    gyro_z = random.uniform(-0.05, 0.05)
    
    vibration = random.uniform(0.5, 3.5)
    
    return {
        "moisture": moisture,
        "accel": {
            "x": accel_x,
            "y": accel_y,
            "z": accel_z
        },
        "gyro": {
            "x": gyro_x,
            "y": gyro_y,
            "z": gyro_z
        },
        "vibration_raw": vibration,
        "timestamp": datetime.now().isoformat()
    }

def send_sensor_data(data):
    """
    센서 데이터를 서버에 전송
    """
    try:
        response = requests.post(SERVER_URL, json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 전송 성공 - Risk Level: {result.get('risk_level', 'N/A')}")
            return True
        else:
            print(f"❌ 전송 실패 - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return False

def main():
    """
    메인 함수
    """
    print("=" * 50)
    print("센서 데이터 전송 시뮬레이터")
    print("=" * 50)
    print(f"서버 URL: {SERVER_URL}")
    print("Ctrl+C로 종료\n")
    
    count = 0
    
    try:
        while True:
            count += 1
            print(f"\n[{count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 데이터 생성 및 전송
            data = generate_sensor_data()
            print(f"  - 토양 수분: {data['moisture']:.1f}")
            print(f"  - 진동: {data['vibration_raw']:.2f}")
            print(f"  - 가속도: ({data['accel']['x']:.3f}, {data['accel']['y']:.3f}, {data['accel']['z']:.3f})")
            
            send_sensor_data(data)
            
            # 3초 대기
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        print(f"총 {count}개의 데이터를 전송했습니다.")

if __name__ == "__main__":
    main()
