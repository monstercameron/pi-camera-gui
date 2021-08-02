import json
from os import path, makedirs

settingsFile = 'settings/camera.settings'
menusFile = 'settings/menu.settings'

def saveSettings(file, dict):
    try:
        with open(file, 'w') as f:
            f.write(json.dumps(dict))
    except Exception as e:
        print(e)

def openSettings(file):
    try:
        with open(file, 'r') as f:
            return json.loads(f.read()) 
    except Exception as e:
        print(e)
        # why???
        saveSettings({})
        return {}

def dcimFolderChecker(settings):
    try:
        if not path.exists(settings['files']['path']):
            makedirs(settings['files']['path'])
    except Exception as e:
        print(e)

def jsonToSettings(json):
    settings = {}
    for key, value in json.items():
        settings[key] = value
    return settings