import pygame
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
        
        # Key Repeat State
        self.pressed_state: Dict[str, int] = {} # key -> start_time
        self.last_repeat: Dict[str, int] = {}   # key -> last_event_time
        
        self.initial_delay = 300 # ms
        self.repeat_interval = 50 # ms

    def listen(self, pygame_mod):
        """
        Polls the hardware buttons and posts Pygame events if pressed.
        """
        current_time = pygame_mod.time.get_ticks()
        
        for key, data in self.buttons.items():
            if data["button"].is_pressed:
                if key not in self.pressed_state:
                    # First Press
                    self.pressed_state[key] = current_time
                    self.last_repeat[key] = current_time
                    
                    evt = pygame_mod.event.Event(pygame_mod.KEYDOWN, key=data["event"])
                    pygame_mod.event.post(evt)
                    print(f"key: '{key}' was pressed")
                else:
                    # Holding
                    duration = current_time - self.pressed_state[key]
                    since_last = current_time - self.last_repeat[key]
                    
                    if duration > self.initial_delay and since_last > self.repeat_interval:
                        evt = pygame_mod.event.Event(pygame_mod.KEYDOWN, key=data["event"])
                        pygame_mod.event.post(evt)
                        # print(f"key: '{key}' repeated")
                        self.last_repeat[key] = current_time
            else:
                # Released
                if key in self.pressed_state:
                    del self.pressed_state[key]
                    if key in self.last_repeat:
                        del self.last_repeat[key]

    def _initialize_buttons(self, settings: Dict[str, Any]):
        self.buttons = {}
        controls = settings.get('controls', {})
        
        for action, config in controls.items():
            key_name = config.get('key')
            pin = config.get('pin')
            
            # Resolve pygame constant
            # We need to handle cases where key_name might be an int (legacy) or string
            if isinstance(key_name, int):
                event_key = key_name
            else:
                event_key = getattr(pygame, key_name, None)
            
            if event_key is None:
                print(f"Warning: Unknown key {key_name} for action {action}")
                continue
            
            # Skip if no pin is assigned (keyboard only)
            if pin is None:
                continue
                
            self.buttons[action] = {
                'button': ButtonClass(pin),
                'description': action,
                'event': event_key
            }
