from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
import socketio
import asyncio
from threading import Thread

SIGNALING_SERVER = 'http://192.168.0.3:8080'
DEVICE_ID = 'caller_device_001'
TARGET_DEVICE = 'receiver_device_001'

class CallerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sio = socketio.Client()
        self.connected = False
        
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        self.status_label = Label(text='Status: Disconnected', size_hint=(1, 0.2))
        layout.add_widget(self.status_label)
        
        # Add camera preview
        self.camera = Camera(play=False, size_hint=(1, 0.6))
        layout.add_widget(self.camera)
        
        self.call_button = Button(text='Connect to Server', size_hint=(1, 0.2))
        self.call_button.bind(on_press=self.connect_server)
        layout.add_widget(self.call_button)
        
        return layout
    
    def connect_server(self, instance):
        Thread(target=self.do_connect).start()
    
    def do_connect(self):
        try:
            self.sio.connect(SIGNALING_SERVER)
            self.sio.emit('register_device', {'device_id': DEVICE_ID})
            self.status_label.text = f'Connected as {DEVICE_ID}'
            self.connected = True
            self.camera.play = True
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'

if __name__ == '__main__':
    CallerApp().run()
