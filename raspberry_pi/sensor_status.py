"""
센서 상태 확인 스크립트
"""

import sys
import subprocess


def check_i2c_devices():
    print("=" * 60)
    print("🔍 I2C 장치 스캔")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ['i2cdetect', '-y', '1'],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        # 주요 장치 확인
        output = result.stdout
        devices_found = []
        
        if '68' in output:
            devices_found.append("MPU6050 (0x68)")
        if '69' in output:
            devices_found.append("MPU6050 (0x69)")
        if '48' in output:
            devices_found.append("ADS1115 (0x48)")
        if '49' in output:
            devices_found.append("ADS1115 (0x49)")
        
        if devices_found:
            print("\n✅ 발견된 장치:")
            for device in devices_found:
                print(f"  - {device}")
        else:
            print("\n⚠️ 주요 센서가 발견되지 않았습니다.")
            print("연결 상태를 확인하세요.")
    
    except FileNotFoundError:
        print("❌ i2cdetect 명령어를 찾을 수 없습니다.")
        print("다음 명령어로 설치하세요:")
        print("  sudo apt install i2c-tools")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ I2C 스캔 실패: {e}")
        print("I2C가 활성화되어 있는지 확인하세요:")
        print("  sudo raspi-config → Interface Options → I2C")


def check_python_packages():
    print("\n" + "=" * 60)
    print("📦 Python 패키지 확인")
    print("=" * 60)
    
    required_packages = [
        'requests',
        'smbus2',
        'adafruit-circuitpython-ads1x15',
        'mpu6050-raspberrypi',
        'numpy'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 설치 필요")


def check_config_file():
    print("\n" + "=" * 60)
    print("⚙️ 설정 파일 확인")
    print("=" * 60)
    
    try:
        from config import (
            SERVER_URL,
            SEND_INTERVAL,
            MPU6050_ADDRESS,
            ADS1115_ADDRESS
        )
        
        print(f"  서버 URL: {SERVER_URL}")
        print(f"  전송 간격: {SEND_INTERVAL}초")
        print(f"  MPU6050 주소: 0x{MPU6050_ADDRESS:02X}")
        print(f"  ADS1115 주소: 0x{ADS1115_ADDRESS:02X}")
        print("\n  ✅ 설정 파일 로드 성공")
    
    except ImportError as e:
        print(f"  ❌ 설정 파일 로드 실패: {e}")


def check_network():
    print("\n" + "=" * 60)
    print("🌐 네트워크 연결 확인")
    print("=" * 60)
    
    try:
        from config import SERVER_URL
        import requests
        from urllib.parse import urlparse
        
        # URL에서 호스트 추출
        parsed = urlparse(SERVER_URL)
        host = parsed.netloc.split(':')[0]
        
        print(f"  서버 호스트: {host}")
        
        # Ping 테스트
        result = subprocess.run(
            ['ping', '-c', '3', host],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✅ {host} 접근 가능")
        else:
            print(f"  ❌ {host} 접근 불가")
            print("  네트워크 연결을 확인하세요.")
        
        # HTTP 테스트
        try:
            response = requests.get(
                f"{parsed.scheme}://{parsed.netloc}/health",
                timeout=5
            )
            if response.status_code == 200:
                print(f"  ✅ 서버 응답 정상")
            else:
                print(f"  ⚠️ 서버 응답 코드: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ 서버 연결 실패: {e}")
    
    except Exception as e:
        print(f"  ❌ 네트워크 확인 실패: {e}")


def main():
    print("\n" + "=" * 60)
    print("🔧 라즈베리파이 센서 시스템 진단")
    print("=" * 60)
    
    check_i2c_devices()
    check_python_packages()
    check_config_file()
    check_network()
    
    print("\n" + "=" * 60)
    print("✅ 진단 완료")
    print("=" * 60)
    print("\n💡 문제가 있다면:")
    print("  1. README.md의 설치 가이드를 확인하세요")
    print("  2. I2C 연결 상태를 점검하세요")
    print("  3. Python 패키지를 다시 설치하세요:")
    print("     pip3 install -r requirements.txt")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
