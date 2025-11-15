from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import asyncio
import socketio
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

SIGNALING_SERVER = 'http://192.168.0.3'
DEVICE_ID = 'receiver_device_001'

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

class ReceiverApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sio = socketio.AsyncClient()
        self.pc = None
        self.camera_track = None
        self.remote_track = None
        
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        self.status_label = Label(text='Status: Waiting for calls...', size_hint=(1, 0.1))
        layout.add_widget(self.status_label)
        
        self.video_widget = Image(size_hint=(1, 0.9))
        layout.add_widget(self.video_widget)
        
        asyncio.ensure_future(self.connect_and_listen())
        
        return layout
    
    async def connect_and_listen(self):
        """Connect to signaling server and listen for calls"""
        try:
            await self.sio.connect(SIGNALING_SERVER)
            await self.sio.emit('register_device', {'device_id': DEVICE_ID})
            
            @self.sio.on('registered')
            async def on_registered(data):
                self.status_label.text = f'Status: Ready - Registered as {data["device_id"]}'
            
            @self.sio.on('incoming_call')
            async def on_incoming_call(data):
                caller_id = data['caller_id']
                auto_accept = data.get('auto_accept', False)
                
                if auto_accept:
                    self.status_label.text = f'Status: Auto-accepting call from {caller_id}'
                    # No user interaction needed - automatically accept
                else:
                    self.status_label.text = f'Status: Call from {caller_id} (not auto-accepted)'
            
            @self.sio.on('webrtc_offer')
            async def on_offer(data):
                # Automatically process offer
                await self.handle_offer(data)
            
        except Exception as e:
            self.status_label.text = f'Connection Error: {str(e)}'
    
    async def handle_offer(self, data):
        """Automatically handle incoming WebRTC offer"""
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
                    self.status_label.text = 'Status: Call Active - Streaming'
            
            # Set remote description
            offer = RTCSessionDescription(
                sdp=data['offer']['sdp'],
                type=data['offer']['type']
            )
            await self.pc.setRemoteDescription(offer)
            
            # Create and send answer
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)
            
            await self.sio.emit('webrtc_answer', {
                'target_id': data['caller_id'],
                'answer': {
                    'sdp': self.pc.localDescription.sdp,
                    'type': self.pc.localDescription.type
                }
            })
            
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

if __name__ == '__main__':
    ReceiverApp().run()
