from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
import requests
import json
from threading import Thread
import time

SIGNALING_SERVER = 'http://192.168.0.3:8080'
DEVICE_ID = 'caller_device_001'
TARGET_DEVICE = 'receiver_device_001'

class CallerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connected = False
        self.session_id = None
        
    def build(self):
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
            Permission.INTERNET
        ])
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.status_label = Label(
            text='Status: Not Connected',
            size_hint=(1, 0.15),
            font_size='18sp'
        )
        layout.add_widget(self.status_label)
        
        # Camera preview
        self.camera = Camera(
            play=False,
            resolution=(640, 480),
            size_hint=(1, 0.65)
        )
        layout.add_widget(self.camera)
        
        # Connect button
        self.connect_btn = Button(
            text='Connect to Server',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.connect_btn.bind(on_press=self.connect_to_server)
        layout.add_widget(self.connect_btn)
        
        # Call button
        self.call_btn = Button(
            text='Start Call',
            size_hint=(1, 0.1),
            disabled=True,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.call_btn.bind(on_press=self.start_call)
        layout.add_widget(self.call_btn)
        
        return layout
    
    def connect_to_server(self, instance):
        """Connect to signaling server"""
        self.status_label.text = 'Status: Connecting...'
        Thread(target=self._connect_thread).start()
    
    def _connect_thread(self):
        try:
            # Test server connectivity
            response = requests.get(SIGNALING_SERVER, timeout=5)
            
            # Register device (simplified REST approach)
            register_data = {
                'device_id': DEVICE_ID,
                'type': 'caller'
            }
            
            Clock.schedule_once(
                lambda dt: self._on_connected(), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self._on_connection_error(str(e)), 0
            )
    
    def _on_connected(self):
        self.connected = True
        self.status_label.text = f'Status: Connected as {DEVICE_ID}'
        self.call_btn.disabled = False
        self.connect_btn.disabled = True
        self.camera.play = True
    
    def _on_connection_error(self, error):
        self.status_label.text = f'Error: {error[:50]}'
        self.call_btn.disabled = True
    
    def start_call(self, instance):
        """Initiate call"""
        self.status_label.text = f'Status: Calling {TARGET_DEVICE}...'
        Thread(target=self._call_thread).start()
    
    def _call_thread(self):
        try:
            # Simulate call initiation
            call_data = {
                'caller_id': DEVICE_ID,
                'receiver_id': TARGET_DEVICE
            }
            
            # In production, send to server endpoint
            time.sleep(1)
            
            Clock.schedule_once(
                lambda dt: self._on_call_started(), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self._on_call_error(str(e)), 0
            )
    
    def _on_call_started(self):
        self.status_label.text = 'Status: Call Active - Camera Streaming'
        self.call_btn.text = 'End Call'
        self.call_btn.background_color = (1, 0.2, 0.2, 1)
    
    def _on_call_error(self, error):
        self.status_label.text = f'Call Error: {error[:50]}'

if __name__ == '__main__':
    CallerApp().run()
