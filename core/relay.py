"""
Relay Controller module for Raspberry Pi GPIO with active-LOW mapping and mock support.
"""

import config

# Try gpiozero first, then RPi.GPIO, then fallback to mock
GPIO_MODE = "mock"
gpio_device = None

if not config.FORCE_SIMULATION:
    try:
        from gpiozero import OutputDevice
        GPIO_MODE = "gpiozero"
    except (ImportError, Exception):
        try:
            import RPi.GPIO as GPIO
            GPIO_MODE = "rpigpio"
        except (ImportError, Exception):
            GPIO_MODE = "mock"


class MotorRelayController:
    def __init__(self, pin=config.RELAY_GPIO_PIN, active_low=config.ACTIVE_LOW_RELAY):
        self.pin = pin
        self.active_low = active_low
        self.mode = GPIO_MODE
        self.state = False  # False = Motor OFF, True = Motor ON
        
        self._init_gpio()

    def _init_gpio(self):
        if self.mode == "gpiozero":
            try:
                from gpiozero import OutputDevice
                # Active LOW: active_high=False means value 1 activates LOW signal
                self.device = OutputDevice(self.pin, active_high=not self.active_low, initial_value=False)
                print(f"[Relay] Initialized GPIO pin {self.pin} via gpiozero.")
            except Exception as e:
                print(f"[Relay] gpiozero init failed: {e}. Using mock mode.")
                self.mode = "mock"
                
        elif self.mode == "rpigpio":
            try:
                import RPi.GPIO as GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin, GPIO.OUT)
                # Initial OFF state (Active LOW -> HIGH is OFF)
                off_val = GPIO.HIGH if self.active_low else GPIO.LOW
                GPIO.output(self.pin, off_val)
                print(f"[Relay] Initialized GPIO pin {self.pin} via RPi.GPIO.")
            except Exception as e:
                print(f"[Relay] RPi.GPIO init failed: {e}. Using mock mode.")
                self.mode = "mock"

        if self.mode == "mock":
            print(f"[Relay] Running in MOCK GPIO mode (Pin {self.pin}).")

    def set_motor(self, state: bool):
        """Set motor state (True = ON, False = OFF). Active-LOW logic supported."""
        self.state = bool(state)
        
        if self.mode == "gpiozero":
            try:
                if self.state:
                    self.device.on()
                else:
                    self.device.off()
            except Exception as e:
                print(f"[Relay] gpiozero write error: {e}")

        elif self.mode == "rpigpio":
            try:
                import RPi.GPIO as GPIO
                # Active LOW: True -> LOW, False -> HIGH
                val = GPIO.LOW if (self.state if self.active_low else not self.state) else GPIO.HIGH
                GPIO.output(self.pin, val)
            except Exception as e:
                print(f"[Relay] RPi.GPIO write error: {e}")

        status_str = "ON (Relay LOW)" if self.state else "OFF (Relay HIGH)"
        print(f"[Relay] Motor state set to {status_str} [Mode: {self.mode}]")

    def cleanup(self):
        """Clean up GPIO channels on shutdown."""
        if self.mode == "rpigpio":
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup(self.pin)
            except Exception:
                pass
        elif self.mode == "gpiozero":
            try:
                self.device.close()
            except Exception:
                pass
