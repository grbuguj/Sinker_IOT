"""
센서 테스트 스크립트
센서 연결 및 데이터 읽기를 테스트합니다.
"""

import time
from sensor_manager import SensorManager


def print_header():
    print("\n" + "=" * 60)
    print("🔍 센서 테스트 모드")
    print("=" * 60)


def print_sensor_status(manager):
    print("\n📊 센서 연결 상태:")
    status = manager.get_status()
    
    print(f"  ADS1115 (ADC): {'✅ 연결됨' if status['ads1115'] else '❌ 연결 안됨'}")
    print(f"  MPU6050 (IMU): {'✅ 연결됨' if status['mpu6050'] else '❌ 연결 안됨'}")
    
    if not all(status.values()):
        print("\n⚠️ 일부 센서가 연결되지 않았습니다.")
        print("   I2C 연결과 주소를 확인하세요.")


def test_continuous_reading(manager, duration=10):
    print(f"\n📡 센서 데이터 연속 읽기 ({duration}초간)")
    print("-" * 60)
    
    start_time = time.time()
    count = 0
    
    try:
        while time.time() - start_time < duration:
            count += 1
            data = manager.read_all()
            
            print(f"\n[{count}] {time.strftime('%H:%M:%S')}")
            print(f"  🌱 토양 수분:     {data['moisture']:>8.1f}")
            print(f"  📳 진동:          {data['vibration_raw']:>8.3f}")
            print(f"  📐 가속도 (m/s²):")
            print(f"     X: {data['accel']['x']:>7.3f}")
            print(f"     Y: {data['accel']['y']:>7.3f}")
            print(f"     Z: {data['accel']['z']:>7.3f}")
            print(f"  🔄 자이로 (deg/s):")
            print(f"     X: {data['gyro']['x']:>7.3f}")
            print(f"     Y: {data['gyro']['y']:>7.3f}")
            print(f"     Z: {data['gyro']['z']:>7.3f}")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⏸️ 사용자가 중단했습니다.")
    
    print(f"\n✅ 총 {count}개 데이터 읽기 완료")


def test_sensor_range(manager):
    print("\n📊 센서 범위 테스트 (10회 샘플링)")
    print("-" * 60)
    
    moisture_values = []
    vibration_values = []
    
    for i in range(10):
        print(f"샘플링 {i+1}/10...", end="\r")
        data = manager.read_all()
        moisture_values.append(data['moisture'])
        vibration_values.append(data['vibration_raw'])
        time.sleep(0.5)
    
    print("\n")
    print(f"🌱 토양 수분:")
    print(f"   최소: {min(moisture_values):.1f}")
    print(f"   최대: {max(moisture_values):.1f}")
    print(f"   평균: {sum(moisture_values)/len(moisture_values):.1f}")
    
    print(f"\n📳 진동:")
    print(f"   최소: {min(vibration_values):.3f}")
    print(f"   최대: {max(vibration_values):.3f}")
    print(f"   평균: {sum(vibration_values)/len(vibration_values):.3f}")


def main():
    print_header()
    
    print("\n⏳ 센서 초기화 중...")
    manager = SensorManager()
    
    print_sensor_status(manager)
    
    print("\n" + "=" * 60)
    print("테스트 메뉴")
    print("=" * 60)
    print("1. 연속 읽기 (10초)")
    print("2. 연속 읽기 (60초)")
    print("3. 센서 범위 테스트")
    print("4. 한 번만 읽기")
    print("0. 종료")
    
    choice = input("\n선택: ").strip()
    
    if choice == "1":
        test_continuous_reading(manager, duration=10)
    elif choice == "2":
        test_continuous_reading(manager, duration=60)
    elif choice == "3":
        test_sensor_range(manager)
    elif choice == "4":
        print("\n📡 센서 데이터 읽기:")
        data = manager.read_all()
        print(f"  토양 수분: {data['moisture']:.1f}")
        print(f"  진동: {data['vibration_raw']:.3f}")
        print(f"  가속도: {data['accel']}")
        print(f"  자이로: {data['gyro']}")
    elif choice == "0":
        print("\n👋 종료합니다.")
    else:
        print("\n❌ 잘못된 선택입니다.")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
