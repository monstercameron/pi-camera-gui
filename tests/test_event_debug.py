"""
Test to check if there's an issue with key repeat or event generation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
import time

pygame.init()

def test_key_repeat_timing():
    """Test the timing of pygame key repeat."""
    print("=== Testing key repeat timing ===")
    print("Key repeat settings: delay=300ms, interval=50ms")
    
    pygame.key.set_repeat(300, 50)
    screen = pygame.display.set_mode((100, 100))
    
    # Simulate holding a key for 1 second
    print("\nSimulating holding UP key for 1 second...")
    
    # Post initial keydown
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    
    start_time = time.time()
    event_count = 0
    
    # Process events for 1 second
    while time.time() - start_time < 1.0:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                event_count += 1
        time.sleep(0.01)  # 10ms sleep
    
    print(f"Events received in 1 second: {event_count}")
    print("Expected with key repeat: ~14 events (1 initial + ~13 repeats after 300ms)")
    
    # The issue: if event_count is MUCH higher, something is wrong
    if event_count > 20:
        print("WARNING: Too many events - possible event generation issue!")
    
    pygame.quit()


def test_check_for_spurious_events():
    """Check if pygame generates events without user input."""
    print("\n=== Checking for spurious events ===")
    
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    pygame.key.set_repeat(300, 50)
    
    print("Waiting 500ms with NO input...")
    
    # Clear any pending events
    pygame.event.get()
    
    time.sleep(0.5)
    
    events = pygame.event.get()
    keydown_events = [e for e in events if e.type == pygame.KEYDOWN]
    
    print(f"Total events: {len(events)}")
    print(f"KEYDOWN events: {len(keydown_events)}")
    
    if keydown_events:
        print("WARNING: Received KEYDOWN events without user input!")
        for e in keydown_events:
            print(f"  Key: {e.key}")
    else:
        print("OK: No spurious KEYDOWN events")
    
    pygame.quit()


def test_webcam_event_interference():
    """Test if webcam operations interfere with pygame events."""
    print("\n=== Testing webcam event interference ===")
    
    pygame.init()
    pygame.camera.init()
    
    screen = pygame.display.set_mode((100, 100))
    pygame.key.set_repeat(300, 50)
    
    # Clear events
    pygame.event.get()
    
    cameras = pygame.camera.list_cameras()
    if not cameras:
        print("No cameras found - skipping webcam test")
        pygame.quit()
        return
    
    print(f"Found camera: {cameras[0]}")
    
    # Start webcam
    webcam = pygame.camera.Camera(cameras[0], (640, 480))
    webcam.start()
    print("Webcam started")
    
    # Check for events
    time.sleep(0.1)
    events = pygame.event.get()
    print(f"Events after webcam start: {len(events)}")
    for e in events:
        print(f"  Event type: {e.type}")
    
    # Stop and restart webcam (like resolution change does)
    webcam.stop()
    print("Webcam stopped")
    
    time.sleep(0.1)
    events = pygame.event.get()
    print(f"Events after webcam stop: {len(events)}")
    for e in events:
        print(f"  Event type: {e.type}")
    
    webcam = pygame.camera.Camera(cameras[0], (1280, 720))
    webcam.start()
    print("Webcam restarted with new resolution")
    
    time.sleep(0.1)
    events = pygame.event.get()
    print(f"Events after webcam restart: {len(events)}")
    for e in events:
        print(f"  Event type: {e.type}")
    
    webcam.stop()
    pygame.quit()


if __name__ == '__main__':
    test_key_repeat_timing()
    test_check_for_spurious_events()
    test_webcam_event_interference()
