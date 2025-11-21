#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서 통합 관리 모듈
동료의 정상 작동 코드 기준으로 리팩토링

센서 구성:
- SW-420 진동센서 (GPIO17)
- 토양수분센서 (MCP3008 SPI CH0)
- MPU6050 기울기/가속도센서 (I2C 0x68)
"""

import RPi.GPIO as GPIO
import spidev
from mpu6050 import mpu6050

from config import (
    VIBRATION_PIN,
    SPI_BUS, SPI_DEVICE, SPI_MAX_SPEED, MOISTURE_CHANNEL,
    MPU6050_ADDRESS
)


class SensorManager:
    """모든 센서를 통합 관리하는 클래스"""
    
    def __init__(self):
        """센서 초기화"""
        # GPIO 설정 (진동 센서)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(VIBRATION_PIN, GPIO.IN)
        print(f">> 1. 진동 센서 설정 완료 (GPIO {VIBRATION_PIN})")
        
        # SPI 설정 (토양 수분 센서)
        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = SPI_MAX_SPEED
        print(f">> 2. 토양 수분 센서 설정 완료 (SPI Bus{SPI_BUS}, Device{SPI_DEVICE})")
        
        # I2C 설정 (기울기/가속도 센서)
        self.gyro_sensor = mpu6050(MPU6050_ADDRESS, bus=20)
        print(f">> 3. 기울기 센서 설정 완료 (I2C 0x{MPU6050_ADDRESS:02X})")
    
    def read_adc(self, channel):
        """
        MCP3008 ADC 값 읽기
        Args:
            channel: 0~7 채널 번호
        Returns:
            int: 0~1023 ADC 값
        """
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data
    
    def read_moisture(self):
        """
        토양 수분 센서 값 읽기
        Returns:
            int: 0~1023 범위의 수분 값
        """
        return self.read_adc(MOISTURE_CHANNEL)
    
    def read_vibration(self):
        """
        진동 센서 현재 상태 읽기
        Returns:
            int: 0 (정지) 또는 1 (진동 감지)
        """
        return GPIO.input(VIBRATION_PIN)
    
    def read_accel(self):
        """
        가속도 센서 값 읽기
        Returns:
            dict: {"x": float, "y": float, "z": float}
        """
        accel_data = self.gyro_sensor.get_accel_data()
        return {
            "x": round(accel_data['x'], 2),
            "y": round(accel_data['y'], 2),
            "z": round(accel_data['z'], 2)
        }
    
    def read_gyro(self):
        """
        자이로스코프 값 읽기
        Returns:
            dict: {"x": float, "y": float, "z": float}
        """
        gyro_data = self.gyro_sensor.get_gyro_data()
        return {
            "x": round(gyro_data['x'], 2),
            "y": round(gyro_data['y'], 2),
            "z": round(gyro_data['z'], 2)
        }
    
    def read_all(self):
        """
        모든 센서 데이터 한 번에 읽기
        Returns:
            dict: 모든 센서 값
        """
        return {
            "moisture": self.read_moisture(),
            "accel": self.read_accel(),
            "gyro": self.read_gyro(),
            "vibration": self.read_vibration()
        }
    
    def cleanup(self):
        """센서 정리 및 종료"""
        print("\n프로그램 종료")
        GPIO.cleanup()
        self.spi.close()


if __name__ == "__main__":
    """직접 실행 시 테스트"""
    print("=" * 50)
    print("센서 매니저 테스트")
    print("=" * 50)
    
    import time
    
    manager = SensorManager()
    
    try:
        for i in range(5):
            print(f"\n[테스트 {i+1}/5]")
            data = manager.read_all()
            print(f"  💧 토양 수분: {data['moisture']}")
            print(f"  🤸 가속도(X,Y,Z): {data['accel']['x']:.2f}, {data['accel']['y']:.2f}, {data['accel']['z']:.2f}")
            print(f"  🔄 자이로(X,Y,Z): {data['gyro']['x']:.2f}, {data['gyro']['y']:.2f}, {data['gyro']['z']:.2f}")
            print(f"  💥 진동: {data['vibration']}")
            time.sleep(1)
    
    except KeyboardInterrupt:
        pass
    
    finally:
        manager.cleanup()
