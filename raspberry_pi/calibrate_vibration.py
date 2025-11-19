"""
진동 센서 캘리브레이션 스크립트
"""

import time
from sensor_manager import SensorManager


def calibrate_vibration():
    print("=" * 60)
    print("📳 진동 센서 캘리브레이션")
    print("=" * 60)
    
    print("\n센서 초기화 중...")
    manager = SensorManager()
    
    if not manager.ads:
        print("❌ ADS1115가 연결되지 않았습니다.")
        return
    
    print("\n✅ 센서 준비 완료")
    
    # 1단계: 정지 상태 측정 (baseline)
    print("\n" + "-" * 60)
    print("1단계: 정지 상태 측정")
    print("-" * 60)
    print("센서를 안정된 표면에 놓고 움직이지 않게 하세요.")
    input("준비되면 Enter를 누르세요...")
    
    print("\n측정 중 (10초간)...")
    baseline_values = []
    for i in range(10):
        value = manager.vibration_sensor.value
        baseline_values.append(value)
        print(f"  [{i+1}/10] ADC 값: {value}")
        time.sleep(1)
    
    baseline_avg = sum(baseline_values) / len(baseline_values)
    print(f"\n✅ 정지 상태 평균 (baseline): {baseline_avg:.0f}")
    
    # 2단계: 진동 테스트
    print("\n" + "-" * 60)
    print("2단계: 진동 테스트")
    print("-" * 60)
    print("센서를 가볍게 두드리거나 흔들어보세요.")
    input("준비되면 Enter를 누르세요...")
    
    print("\n측정 중 (10초간)...")
    print("센서를 흔들어보세요!")
    vibration_values = []
    for i in range(10):
        value = manager.vibration_sensor.value
        vibration_values.append(value)
        delta = abs(value - baseline_avg)
        print(f"  [{i+1}/10] ADC: {value} | 변화량: {delta:.0f}")
        time.sleep(1)
    
    max_vibration = max([abs(v - baseline_avg) for v in vibration_values])
    print(f"\n✅ 최대 진동 변화량: {max_vibration:.0f}")
    
    # 권장 스케일 계산
    if max_vibration > 0:
        recommended_scale = 1000.0 / max_vibration
    else:
        recommended_scale = 1.0
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("📊 캘리브레이션 결과")
    print("=" * 60)
    print(f"VIBRATION_BASELINE = {baseline_avg:.0f}")
    print(f"VIBRATION_SCALE = {recommended_scale:.6f}")
    print(f"\n권장 임계값:")
    print(f"  주의 (warning): 1.0")
    print(f"  위험 (danger): 2.0")
    
    print("\n" + "=" * 60)
    print("📝 다음 단계:")
    print("=" * 60)
    print("1. config.py 파일을 열기")
    print("2. 다음 값을 업데이트:")
    print(f"   VIBRATION_BASELINE = {baseline_avg:.0f}")
    print(f"   VIBRATION_SCALE = {recommended_scale:.6f}")
    print("3. 파일 저장 후 센서 클라이언트 재시작")
    print("=" * 60)


if __name__ == "__main__":
    calibrate_vibration()
