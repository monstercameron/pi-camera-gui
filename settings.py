import json
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
    except:
        saveSettings({})
        return {}

def jsonToSettings(json):
    settings = {}
    for key, value in json.items():
        settings[key] = value
    return settings