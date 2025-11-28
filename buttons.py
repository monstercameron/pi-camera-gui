import pygame.locals
from gpio_manager import get_button_class
from time import sleep

# Get the appropriate Button class (Real or Mock)
Button = get_button_class()

class Buttons:
    def __init__(self, settings):
        self.buttons = None
        self.buttonsFromSettings(settings)
        # print(self.buttons)

    def listen(self, pygame):
        for key in self.buttons.keys():
            if self.buttons[key]["button"].is_pressed:
                evt = pygame.event.Event(
                    pygame.KEYDOWN, key=self.buttons[key]["event"])
                pygame.event.post(evt)
                print(f"key: '{key}' was pressed")
                sleep(.25)

    def buttonsFromSettings(self, settings):
        # try:
        # reset all buttons
        self.buttons = {}
        # print(settings['buttons'])
        for obj in settings['buttons']:
            # print(obj['name'])
            self.buttons[obj["name"]] = {'button': Button(
                obj["gpio"]), 'description': obj["description"], 'event': obj["event"]}
        return self.buttons
        # except Exception:
        #     print("error importing button configurations")
        #     print(Exception)
        
