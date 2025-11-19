"""
센서 매니저 - 모든 센서 데이터 읽기 통합
"""

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from mpu6050 import mpu6050
import numpy as np
from collections import deque
from config import (
    MPU6050_ADDRESS,
    ADS1115_ADDRESS,
    MOISTURE_CHANNEL,
    VIBRATION_CHANNEL,
    MOISTURE_DRY,
    MOISTURE_WET,
    VIBRATION_BASELINE,
    VIBRATION_SCALE,
    MOVING_AVERAGE_WINDOW
)


class SensorManager:
    """
    모든 센서를 관리하는 클래스
    """
    
    def __init__(self):
        """
        센서 초기화
        """
        print("🔧 센서 초기화 중...")
        
        # I2C 버스 초기화
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # ADS1115 초기화 (아날로그 센서용)
        try:
            self.ads = ADS.ADS1115(self.i2c, address=ADS1115_ADDRESS)
            self.moisture_sensor = AnalogIn(self.ads, MOISTURE_CHANNEL)
            self.vibration_sensor = AnalogIn(self.ads, VIBRATION_CHANNEL)
            print("✅ ADS1115 초기화 완료")
        except Exception as e:
            print(f"❌ ADS1115 초기화 실패: {e}")
            self.ads = None
        
        # MPU6050 초기화 (가속도계 + 자이로스코프)
        try:
            self.mpu = mpu6050(MPU6050_ADDRESS)
            print("✅ MPU6050 초기화 완료")
        except Exception as e:
            print(f"❌ MPU6050 초기화 실패: {e}")
            self.mpu = None
        
        # 이동 평균을 위한 버퍼
        self.moisture_buffer = deque(maxlen=MOVING_AVERAGE_WINDOW)
        self.vibration_buffer = deque(maxlen=MOVING_AVERAGE_WINDOW)
        
        print("✅ 센서 초기화 완료!\n")
    
    def read_moisture(self):
        """
        토양 수분 센서 읽기
        Returns: float (0~1000, 캘리브레이션된 값)
        """
        if not self.ads:
            return 0.0
        
        try:
            # ADC 값 읽기
            raw_value = self.moisture_sensor.value
            
            # 캘리브레이션 적용 (0~1000 스케일)
            if MOISTURE_DRY != MOISTURE_WET:
                # 반비례 관계 (값이 낮을수록 습함)
                moisture = 1000 * (1 - (raw_value - MOISTURE_WET) / (MOISTURE_DRY - MOISTURE_WET))
                moisture = max(0, min(1000, moisture))  # 0~1000 범위 제한
            else:
                moisture = raw_value / 32767.0 * 1000
            
            # 이동 평균 적용
            self.moisture_buffer.append(moisture)
            return np.mean(self.moisture_buffer)
        
        except Exception as e:
            print(f"⚠️ 토양 수분 센서 읽기 실패: {e}")
            return 0.0
    
    def read_vibration(self):
        """
        진동 센서 읽기
        Returns: float (진동 강도)
        """
        if not self.ads:
            return 0.0
        
        try:
            # ADC 값 읽기
            raw_value = self.vibration_sensor.value
            
            # 캘리브레이션 적용
            vibration = (raw_value - VIBRATION_BASELINE) * VIBRATION_SCALE
            vibration = abs(vibration) / 10000.0  # 정규화
            
            # 이동 평균 적용
            self.vibration_buffer.append(vibration)
            return np.mean(self.vibration_buffer)
        
        except Exception as e:
            print(f"⚠️ 진동 센서 읽기 실패: {e}")
            return 0.0
    
    def read_accel(self):
        """
        가속도 센서 읽기
        Returns: dict {"x": float, "y": float, "z": float}
        """
        if not self.mpu:
            return {"x": 0.0, "y": 0.0, "z": 9.8}
        
        try:
            accel_data = self.mpu.get_accel_data()
            return {
                "x": round(accel_data['x'], 3),
                "y": round(accel_data['y'], 3),
                "z": round(accel_data['z'], 3)
            }
        except Exception as e:
            print(f"⚠️ 가속도 센서 읽기 실패: {e}")
            return {"x": 0.0, "y": 0.0, "z": 9.8}
    
    def read_gyro(self):
        """
        자이로스코프 센서 읽기
        Returns: dict {"x": float, "y": float, "z": float}
        """
        if not self.mpu:
            return {"x": 0.0, "y": 0.0, "z": 0.0}
        
        try:
            gyro_data = self.mpu.get_gyro_data()
            return {
                "x": round(gyro_data['x'], 3),
                "y": round(gyro_data['y'], 3),
                "z": round(gyro_data['z'], 3)
            }
        except Exception as e:
            print(f"⚠️ 자이로 센서 읽기 실패: {e}")
            return {"x": 0.0, "y": 0.0, "z": 0.0}
    
    def read_all(self):
        """
        모든 센서 데이터 읽기
        Returns: dict
        """
        return {
            "moisture": self.read_moisture(),
            "accel": self.read_accel(),
            "gyro": self.read_gyro(),
            "vibration_raw": self.read_vibration()
        }
    
    def get_status(self):
        """
        센서 연결 상태 확인
        Returns: dict
        """
        return {
            "ads1115": self.ads is not None,
            "mpu6050": self.mpu is not None
        }


if __name__ == "__main__":
    """
    테스트용 코드
    """
    print("=" * 50)
    print("센서 매니저 테스트")
    print("=" * 50)
    
    manager = SensorManager()
    
    print("\n센서 상태:")
    status = manager.get_status()
    for sensor, connected in status.items():
        status_text = "✅ 연결됨" if connected else "❌ 연결 안됨"
        print(f"  {sensor}: {status_text}")
    
    print("\n센서 데이터 읽기 (5초간):")
    for i in range(5):
        print(f"\n[{i+1}/5]")
        data = manager.read_all()
        print(f"  토양 수분: {data['moisture']:.1f}")
        print(f"  진동: {data['vibration_raw']:.3f}")
        print(f"  가속도: X={data['accel']['x']:.3f}, Y={data['accel']['y']:.3f}, Z={data['accel']['z']:.3f}")
        print(f"  자이로: X={data['gyro']['x']:.3f}, Y={data['gyro']['y']:.3f}, Z={data['gyro']['z']:.3f}")
        time.sleep(1)
    
    print("\n✅ 테스트 완료!")
