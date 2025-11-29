# Getting Started with PiCameraGUI

PiCameraGUI is a Python-based graphical user interface for the Raspberry Pi Camera Module, built using Pygame. It provides a touch-friendly (or button-navigable) interface to control camera settings like ISO, shutter speed, AWB, and effects, and to capture images.

## Table of Contents
1.  [Prerequisites](#prerequisites)
2.  [Installation](#installation)
3.  [Configuration](#configuration)
4.  [Running the Application](#running-the-application)
5.  [Controls](#controls)
6.  [Development and Testing](#development-and-testing)
7.  [Extending the Application](#extending-the-application)
8.  [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware
*   **Raspberry Pi**: Tested on Raspberry Pi 3/4/Zero.
*   **Camera Module**: Raspberry Pi Camera Module v1, v2, or HQ Camera.
*   **Display**: A screen connected via HDMI or DSI (e.g., HyperPixel, official 7" Touchscreen).
*   **Input**: Physical buttons (GPIO) or Keyboard (for development/testing).

### Software
*   **OS**: Raspberry Pi OS (Legacy/Buster recommended for `picamera` support, or Bullseye/Bookworm with legacy camera stack enabled).
*   **Python**: 3.7+
*   **Libraries**:
    *   `pygame` (or `pygame-ce`)
    *   `picamera` (for hardware access)
    *   `Pillow` (optional, for software encoding and EXIF metadata)

---

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/pi-camera-gui.git
    cd pi-camera-gui
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: On Raspberry Pi, you might need to install system dependencies for pygame and picamera.*

---

## Configuration

The application is highly configurable via JSON and XML files located in the root or `src/ui/layouts/` directories.

### 1. Camera Settings (`camerasettings.json`)
Controls default camera parameters and file paths.
```json
{
    "files": {
        "path": "/home/pi/images",
        "template": "img_{}_{}"
    },
    "display": {
        "width": 800,
        "height": 480,
        "fullscreen": true
    }
}
```

### 2. Menu Structure (`menusettings.json`)
Defines the menu hierarchy. You can add new menus or options here.
*   **`name`**: The internal ID of the menu item.
*   **`type`**: `list` (submenu or choice) or `range` (slider).
*   **`options`**: List of choices or min/max values.

### 3. Visual Layout (`src/ui/layouts/default.xml`)
Defines the visual layout (position, size, colors) of the UI elements using XML.
*   **`<container id="level_0">`**: Main menu column.
*   **`<container id="stats">`**: Top/Bottom status bar.

---

## Running the Application

### On Raspberry Pi (Production)
Run the application directly with Python:
```bash
python run.py
```
This will attempt to initialize the PiCamera and the display.

### On PC / Development (Mock Mode)
You can run the application on a PC (Windows/Linux/Mac) without a Pi Camera. The application will automatically detect the missing hardware and switch to **Mock Mode**.

*   **Mock Camera**: Simulates camera behavior (uses a webcam if available, or generates placeholder images).
*   **Mock GPIO**: Simulates button presses via keyboard keys.

To run in a windowed mode on PC:
```bash
python run.py
```

### Headless / No Display
If you want to run the application logic without a video window (e.g., for testing logic via SSH), you can set the video driver to a headless one:

**Linux/Mac:**
```bash
export SDL_VIDEODRIVER=null
python run.py
```

**Windows (PowerShell):**
```powershell
$env:SDL_VIDEODRIVER='null'
python run.py
```

---

## Controls

### Keyboard (Mock Mode)
*   **Arrow Keys**: Navigate menus (Up/Down/Left/Right).
*   **Enter**: Select / Toggle Menu.
*   **Space**: Capture Image.
*   **Esc**: Back / Exit.

### GPIO Buttons (Default Mapping)
*   **Pin 17**: Menu / Select
*   **Pin 27**: Back
*   **Pin 22**: Up
*   **Pin 23**: Down
*   **Pin 24**: Capture

*(Note: Pin mappings can be configured in `src/hardware/buttons.py` or config files if implemented)*

---

## Development and Testing

The project includes a comprehensive test suite to ensure stability and prevent regressions.

### Running Unit Tests
To run the full test suite, execute the following command from the project root:
```bash
python -m unittest discover tests
```

This will run all tests located in the `tests/` directory, including:
*   **Core Logic**: Configuration, Database, and Settings management.
*   **UI Components**: Layout parsing, Menu rendering, and Navigation logic.
*   **Hardware Abstraction**: Mock Camera and Button behavior.
*   **Performance**: Render loop efficiency and caching verification.

### Running Specific Tests
You can run individual test files to focus on specific components:
```bash
# Test UI Logic
python -m unittest tests/test_ui.py

# Test Performance
python -m unittest tests/test_performance_gui.py
```

### Mock Architecture
The tests use `unittest.mock` to simulate hardware dependencies (`picamera`, `pygame`, `RPi.GPIO`). This allows the entire suite to run on any development machine (Windows/Mac/Linux) without requiring actual Raspberry Pi hardware.

*   **MockCamera**: Simulates camera operations and image capture.
*   **MockButton**: Simulates GPIO input events.
*   **MockPygame**: Simulates the display surface and event loop for headless testing.

---

## Extending the Application

PiCameraGUI is designed to be modular. You can extend it to support new cameras, input devices, or menu options.

### 1. Adding a New Camera Backend

The application uses an abstract base class `CameraBase` defined in `src/hardware/camera.py`. To support a new camera (e.g., a DSLR via gphoto2, or a USB webcam via OpenCV):

1.  **Create a New Class**: Create a new class in `src/hardware/camera.py` (or a new file) that inherits from `CameraBase`.
2.  **Implement Abstract Methods**: You must implement the following methods:
    *   `startPreview()`: Initialize and start the live view.
    *   `stopPreview()`: Stop the live view.
    *   `captureImage()`: Capture a still image to disk.
    *   `get_supported_options(key)`: Return valid values for settings like ISO or shutter speed.
    *   `render(surface)`: Draw the camera feed onto the Pygame surface (if not using a hardware overlay).
3.  **Register the Camera**: Update the `get_camera()` factory function in `src/hardware/camera.py` to instantiate your new class based on a configuration flag or auto-detection.

### 2. Adding New Input Devices

The GUI is event-driven and relies on standard Pygame events.

*   **GPIO Buttons**: Configured in `src/hardware/buttons.py`. The `Buttons` class polls `gpiozero` buttons and posts `pygame.KEYDOWN` events. To add more buttons, simply add them to the `buttons` list in `camerasettings.json` with their GPIO pin and corresponding Pygame key code.
*   **Rotary Encoders / Joysticks**: To add complex inputs:
    1.  Create a new hardware interface class (similar to `Buttons`).
    2.  In its `listen()` loop, read the hardware state.
    3.  Translate the hardware action into a Pygame event:
        ```python
        # Example: Posting an event when a dial turns
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        pygame.event.post(event)
        ```
    4.  Instantiate your class in `run.py` and call its listener in the main loop.

### 3. Adding New Menu Options

To add a new setting (e.g., "HDR Mode"):

1.  **Update `menusettings.json`**: Add the new option to the desired menu.
    ```json
    {
        "name": "hdr_mode",
        "type": "list",
        "options": ["off", "on", "auto"]
    }
    ```
2.  **Update `CameraBase`**: Add the logic to handle this setting in `src/hardware/camera.py`.
    *   Add a method `hdr_mode(self, value=None)` to get/set the value.
    *   Add `"hdr_mode": self.hdr_mode` to the dictionary returned by `directory()`.
3.  **Implement in RealCamera**: Add the actual hardware call in `RealCamera.hdr_mode`.

---

## Troubleshooting

*   **"picamera module not found"**: You are running on a non-Pi device or haven't installed the library. The app will fallback to Mock Mode.
*   **No Window Visible**: Check your `SDL_VIDEODRIVER` environment variable. If it's set to `null` or `rpi` on a PC, you won't see a window. Unset it to fix:
    *   Linux: `unset SDL_VIDEODRIVER`
    *   Windows: `$env:SDL_VIDEODRIVER=$null`
*   **Permission Errors**: Ensure the user has permissions to access the camera interface (`raspi-config` -> Interface Options -> Camera).

## License
[License Name Here]
