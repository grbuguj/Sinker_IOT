#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서 테스트 프로그램
동료의 정상 작동 코드 기준 - 로컬에서 센서 값만 출력

실행 방법:
    python3 sensor_test.py
    
종료:
    Ctrl+C
"""

import RPi.GPIO as GPIO
import time
from sensor_manager import SensorManager
from config import VIBRATION_PIN, BOUNCE_TIME


# 진동 감지 콜백 함수
def vibration_detected(channel):
    """진동 감지 시 실행되는 함수"""
    print("\n\n🚨 [경고] 진동(움직임)이 감지되었습니다! 🚨\n")


def main():
    """메인 함수"""
    print("=" * 60)
    print("모든 센서 모니터링 시작")
    print("=" * 60)
    
    # 센서 매니저 초기화
    manager = SensorManager()
    
    # 진동 센서 이벤트 리스너 등록
    GPIO.add_event_detect(
        VIBRATION_PIN,
        GPIO.RISING,
        callback=vibration_detected,
        bouncetime=BOUNCE_TIME
    )
    print(">> 진동 센서 이벤트 대기 중 (이벤트 기반)\n")
    print("진동이 발생하면 즉시 경고 메시지가 뜹니다.")
    print("Ctrl+C로 종료하세요.\n")
    
    try:
        while True:
            # 토양 수분 값 읽기
            moist_val = manager.read_moisture()
            
            # 기울기/가속도 값 읽기
            accel_data = manager.read_accel()
            gyro_data = manager.read_gyro()
            
            # 진동 센서 현재 상태 읽기
            vibration_state = manager.read_vibration()
            
            # 화면 출력
            print("-" * 60)
            print(f"💧 토양 수분   : {moist_val}")
            print(f"🤸 가속도(X,Y,Z): {accel_data['x']:.2f}, {accel_data['y']:.2f}, {accel_data['z']:.2f}")
            print(f"🔄 자이로(X,Y,Z): {gyro_data['x']:.2f}, {gyro_data['y']:.2f}, {gyro_data['z']:.2f}")
            print(f"💥 진동 감지값  : {vibration_state}")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        pass
    
    finally:
        manager.cleanup()
        print("✅ 테스트 완료!")


if __name__ == "__main__":
    main()
