"""
토양 수분 센서 캘리브레이션 스크립트
"""

import time
from sensor_manager import SensorManager


def calibrate_moisture():
    print("=" * 60)
    print("🌱 토양 수분 센서 캘리브레이션")
    print("=" * 60)
    
    print("\n센서 초기화 중...")
    manager = SensorManager()
    
    if not manager.ads:
        print("❌ ADS1115가 연결되지 않았습니다.")
        return
    
    print("\n✅ 센서 준비 완료")
    
    # 1단계: 건조 상태 측정
    print("\n" + "-" * 60)
    print("1단계: 건조 상태 측정")
    print("-" * 60)
    print("센서를 건조한 공기에 노출시키세요.")
    input("준비되면 Enter를 누르세요...")
    
    print("\n측정 중 (5초간)...")
    dry_values = []
    for i in range(5):
        value = manager.moisture_sensor.value
        dry_values.append(value)
        print(f"  [{i+1}/5] ADC 값: {value}")
        time.sleep(1)
    
    dry_avg = sum(dry_values) / len(dry_values)
    print(f"\n✅ 건조 상태 평균: {dry_avg:.0f}")
    
    # 2단계: 습윤 상태 측정
    print("\n" + "-" * 60)
    print("2단계: 습윤 상태 측정")
    print("-" * 60)
    print("센서를 물에 담그세요. (센서 끝부분만, 회로 부분은 X)")
    input("준비되면 Enter를 누르세요...")
    
    print("\n측정 중 (5초간)...")
    wet_values = []
    for i in range(5):
        value = manager.moisture_sensor.value
        wet_values.append(value)
        print(f"  [{i+1}/5] ADC 값: {value}")
        time.sleep(1)
    
    wet_avg = sum(wet_values) / len(wet_values)
    print(f"\n✅ 습윤 상태 평균: {wet_avg:.0f}")
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("📊 캘리브레이션 결과")
    print("=" * 60)
    print(f"MOISTURE_DRY = {dry_avg:.0f}")
    print(f"MOISTURE_WET = {wet_avg:.0f}")
    
    print("\n" + "=" * 60)
    print("📝 다음 단계:")
    print("=" * 60)
    print("1. config.py 파일을 열기")
    print("2. 다음 값을 업데이트:")
    print(f"   MOISTURE_DRY = {dry_avg:.0f}")
    print(f"   MOISTURE_WET = {wet_avg:.0f}")
    print("3. 파일 저장 후 센서 클라이언트 재시작")
    print("=" * 60)


if __name__ == "__main__":
    calibrate_moisture()
