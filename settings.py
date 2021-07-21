import json
settings_file = 'settings/camera.settings'


def save(settings):
    with open(settings_file, 'w') as f:
        f.write(json.dumps(settings))

def open():
    with open(settings_file, 'r') as f:
        settings = json.loads(f.read())
    return settings