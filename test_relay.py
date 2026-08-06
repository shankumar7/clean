import urllib.request
import time

def test_relay():
    print("1. Telling ESP32 to enter MANUAL MODE...")
    try:
        response = urllib.request.urlopen("http://192.168.4.1/setMode?manual=1", timeout=2)
        print(f"   -> Success! ESP32 says: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"   -> ERROR connecting to ESP32: {e}")
        return

    time.sleep(1)

    print("\n2. Sending MOTOR ON command to ESP32...")
    try:
        response = urllib.request.urlopen("http://192.168.4.1/toggleMotor?state=1", timeout=2)
        print(f"   -> Success! Motor should be ON. ESP32 says: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"   -> ERROR connecting to ESP32: {e}")

    time.sleep(3)

    print("\n3. Sending MOTOR OFF command to ESP32...")
    try:
        response = urllib.request.urlopen("http://192.168.4.1/toggleMotor?state=0", timeout=2)
        print(f"   -> Success! Motor should be OFF. ESP32 says: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"   -> ERROR connecting to ESP32: {e}")

if __name__ == "__main__":
    print("=== ESP32 RELAY TEST SCRIPT ===")
    test_relay()
    print("===============================")
