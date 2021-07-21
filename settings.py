import json
settings_file = 'settings/camera.settings'


def saveSettings(settings):
    try:
        with open(settings_file, 'w') as f:
            f.write(json.dumps(settings))
    except Exception as e:
        print(e)

def openSettings():
    try:
        
        with open(settings_file, 'r') as f:
            return json.loads(f.read()) 
    except:
        saveSettings({})
        return {}

def jsonToSettings(json):
    settings = {}
    for key, value in json.items():
        settings[key] = value
    return settings