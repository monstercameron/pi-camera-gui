# 📸 Pi Camera GUI

**The fun, menu-driven interface for your Raspberry Pi High Quality Camera!**

Built with **Pygame**, this project turns your Raspberry Pi into a proper digital camera with a slick, navigable UI. Whether you're snapping photos in the field or testing on your desktop, we've got you covered.

## ✨ Features

*   **Slick UI**: A responsive, menu-driven interface that feels like a real camera.
*   **Deep Control**: Tweak everything from **ISO** and **Shutter Speed** to **AWB** and **Image Effects**.
*   **Rich Metadata**: Your photos aren't just pixels; they come packed with **EXIF data** (Lens info, Copyright, XP Tags).
*   **Mock Mode**: No Pi? No problem! Run it on your PC using your webcam to test the UI.
*   **Persistent Settings**: We remember your tweaks using a local SQLite database.
*   **Reset Button**: Messed up your settings? Hit the "Reset Settings" option to go back to fresh defaults.

## 🚀 Getting Started

### Prerequisites
*   Python 3.x
*   A Raspberry Pi with a Camera Module (or a webcam for Mock Mode)

### Installation

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/yourusername/pi-camera-gui.git
    cd pi-camera-gui
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run it!**
    ```bash
    python run.py
    ```
    *Note: On a desktop without a Pi Camera, it automatically switches to **Mock Mode** and uses your webcam!*

## 🎮 Controls

Navigate the UI like a pro. (Default keyboard mappings, customizable in `home/config/camerasettings.json`)

| Action | Key | Description |
| :--- | :--- | :--- |
| **Menu / Back** | `Enter` | Toggle the menu overlay |
| **Capture** | `Space` | Snap a photo! |
| **Up / Down** | `Arrow Keys` | Navigate lists or adjust values |
| **Left / Right** | `Arrow Keys` | Enter/Exit submenus |
| **Quick Stats** | `Arrows` | Cycle stats when menu is closed |

## 📂 Where's my stuff?

We keep your data organized in the `home/` directory:
*   **`home/dcim/`**: Your captured masterpieces go here.
*   **`home/config/`**: Configuration files and your settings database.

## 🛠️ Development

Want to hack on it?
*   **`src/`**: The source code.
*   **`tests/`**: Test scripts to verify camera resolution and EXIF tags.

---
*Happy Snapping!* 📷