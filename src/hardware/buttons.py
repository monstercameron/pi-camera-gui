import pygame
from time import sleep
from typing import Dict, Any, Type
from src.core.config import config

try:
    import gpiozero
except ImportError:
    gpiozero = None

class MockButton:
    def __init__(self, pin: int, bounce_time: float = None):
        self.pin = pin
        self.is_pressed = False
        print(f"MockButton initialized on pin {pin}")

    def when_pressed(self):
        pass

    def when_released(self):
        pass

def get_button_class() -> Type:
    if config.USE_MOCK_GPIO:
        print("Using MockButton (Configured or Auto-detected)")
        return MockButton
    
    try:
        if gpiozero:
            return gpiozero.Button
        else:
            return MockButton
    except Exception as e:
        print(f"Error loading gpiozero Button: {e}. Falling back to MockButton.")
        return MockButton

# Get the appropriate Button class (Real or Mock)
ButtonClass = get_button_class()

class Buttons:
    def __init__(self, settings: Dict[str, Any]):
        self.buttons: Dict[str, Any] = {}
        self._initialize_buttons(settings)

    def listen(self, pygame_mod):
        """
        Polls the hardware buttons and posts Pygame events if pressed.
        """
        for key, data in self.buttons.items():
            if data["button"].is_pressed:
                evt = pygame_mod.event.Event(
                    pygame_mod.KEYDOWN, key=data["event"])
                pygame_mod.event.post(evt)
                print(f"key: '{key}' was pressed")
                sleep(0.25) # Debounce / Repeat delay

    def _initialize_buttons(self, settings: Dict[str, Any]):
        self.buttons = {}
        for obj in settings['buttons']:
            self.buttons[obj["name"]] = {
                'button': ButtonClass(obj["gpio"]), 
                'description': obj["description"], 
                'event': obj["event"]
            }
