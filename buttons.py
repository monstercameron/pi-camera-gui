import pygame.locals
from gpiozero import Button
from time import sleep


class Buttons:
    def __init__(self, settings):
        self.pressed = False
        self.buttons = {}
        self.buttonsFromSettings(settings)
        # print(self.buttons)

    def listen(self, pygame):
        for key in self.buttons.keys():
            if self.buttons[key]["button"].is_pressed and not self.pressed:
                evt = pygame.event.Event(
                    pygame.KEYDOWN, key=self.buttons[key]["event"])

                pygame.event.post(evt)
                print(f"key: '{key}' was pressed")
                self.pressed = not self.pressed
                sleep(.25)
            else:
                self.pressed = not self.pressed

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
