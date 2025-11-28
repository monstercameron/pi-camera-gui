try:
    import gpiozero
    # Check if we can actually initialize a pin factory (fails on Windows)
    try:
        from gpiozero.pins.native import NativeFactory
        # This is a bit of a hack, but gpiozero tries to load a factory on import/usage
        # On Windows, it will fail unless we are very careful.
        # The safest check is often just OS check or try/except on usage.
    except ImportError:
        pass
except ImportError:
    gpiozero = None

import os

class MockButton:
    def __init__(self, pin, bounce_time=None):
        self.pin = pin
        self.is_pressed = False
        print(f"MockButton initialized on pin {pin}")

    def when_pressed(self):
        pass

    def when_released(self):
        pass

def get_button_class():
    # Force mock on Windows or if gpiozero is missing
    if os.name == 'nt' or gpiozero is None:
        print("Using MockButton (Windows or gpiozero missing)")
        return MockButton
    
    try:
        # Try to initialize a dummy button to see if the factory works
        # This catches cases where gpiozero is installed but no GPIO access (e.g. non-Pi Linux)
        # However, for now, we will trust the import if not on Windows.
        return gpiozero.Button
    except Exception as e:
        print(f"Error loading gpiozero Button: {e}. Falling back to MockButton.")
        return MockButton
