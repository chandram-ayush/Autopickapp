from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import asyncio
import socketio
import cv2
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame
import numpy as np

SIGNALING_SERVER = 'http://192.168.0.3'
DEVICE_ID = 'caller_device_001'
TARGET_DEVICE = 'receiver_device_001'

class CameraTrack(VideoStreamTrack):
    """Custom video track from camera"""
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
    
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
            video_frame.pts = pts
            video_frame.time_base = time_base
            return video_frame
    
    def stop(self):
        self.cap.release()

class CallerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sio = socketio.AsyncClient()
        self.pc = None
        self.camera_track = None
        self.remote_track = None
        self.connected = False
        
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        self.status_label = Label(text='Status: Disconnected', size_hint=(1, 0.1))
        layout.add_widget(self.status_label)
        
        self.video_widget = Image(size_hint=(1, 0.7))
        layout.add_widget(self.video_widget)
        
        self.call_button = Button(text='Start Call', size_hint=(1, 0.1))
        self.call_button.bind(on_press=self.start_call)
        layout.add_widget(self.call_button)
        
        self.hangup_button = Button(text='Hang Up', size_hint=(1, 0.1), disabled=True)
        self.hangup_button.bind(on_press=self.hang_up)
        layout.add_widget(self.hangup_button)
        
        asyncio.ensure_future(self.connect_signaling())
        
        return layout
    
    async def connect_signaling(self):
        """Connect to signaling server"""
        try:
            await self.sio.connect(SIGNALING_SERVER)
            await self.sio.emit('register_device', {'device_id': DEVICE_ID})
            
            @self.sio.on('registered')
            async def on_registered(data):
                self.status_label.text = f'Status: Registered as {data["device_id"]}'
                self.connected = True
            
            @self.sio.on('webrtc_answer')
            async def on_answer(data):
                answer = RTCSessionDescription(
                    sdp=data['answer']['sdp'],
                    type=data['answer']['type']
                )
                await self.pc.setRemoteDescription(answer)
                self.status_label.text = 'Status: Call Connected'
            
            @self.sio.on('ice_candidate')
            async def on_ice(data):
                # Handle ICE candidates if needed
                pass
                
        except Exception as e:
            self.status_label.text = f'Connection Error: {str(e)}'
    
    def start_call(self, instance):
        """Initiate call to receiver"""
        if not self.connected:
            self.status_label.text = 'Error: Not connected to server'
            return
        
        asyncio.ensure_future(self.setup_webrtc())
        
    async def setup_webrtc(self):
        """Setup WebRTC connection"""
        try:
            self.pc = RTCPeerConnection()
            
            # Add camera track
            self.camera_track = CameraTrack()
            self.pc.addTrack(self.camera_track)
            
            # Handle incoming tracks
            @self.pc.on("track")
            async def on_track(track):
                if track.kind == "video":
                    self.remote_track = track
                    Clock.schedule_interval(self.update_video, 1.0/30.0)
            
            # Create and send offer
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            
            await self.sio.emit('call_device', {'receiver_id': TARGET_DEVICE})
            await self.sio.emit('webrtc_offer', {
                'target_id': TARGET_DEVICE,
                'caller_id': DEVICE_ID,
                'offer': {
                    'sdp': self.pc.localDescription.sdp,
                    'type': self.pc.localDescription.type
                }
            })
            
            self.status_label.text = 'Status: Calling...'
            self.call_button.disabled = True
            self.hangup_button.disabled = False
            
        except Exception as e:
            self.status_label.text = f'Call Error: {str(e)}'
    
    def update_video(self, dt):
        """Update video display"""
        if self.remote_track:
            try:
                frame = asyncio.run(self.remote_track.recv())
                img = frame.to_ndarray(format="rgb24")
                
                texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb')
                texture.blit_buffer(img.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
                texture.flip_vertical()
                self.video_widget.texture = texture
            except:
                pass
    
    def hang_up(self, instance):
        """End call"""
        if self.pc:
            asyncio.ensure_future(self.pc.close())
        if self.camera_track:
            self.camera_track.stop()
        
        self.status_label.text = 'Status: Call Ended'
        self.call_button.disabled = False
        self.hangup_button.disabled = True
        Clock.unschedule(self.update_video)

if __name__ == '__main__':
    CallerApp().run()
