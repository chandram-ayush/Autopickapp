from aiohttp import web
import socketio
import json

# Store connected devices
devices = {}
# Whitelist of allowed device pairs (caller_id: [allowed_receiver_ids])
DEVICE_WHITELIST = {
    'caller_device_001': ['receiver_device_001'],
    'receiver_device_001': ['caller_device_001']
}

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
app = web.Application()
sio.attach(app)

async def index(request):
    return web.Response(text='Signaling Server is Running! Connected devices: {}'.format(len(devices)))

app.router.add_get('/', index)  

@sio.event
async def connect(sid, environ):
    print(f'Client connected: {sid}')

@sio.event
async def disconnect(sid):
    print(f'Client disconnected: {sid}')
    # Remove device from connected devices
    device_to_remove = None
    for device_id, device_sid in devices.items():
        if device_sid == sid:
            device_to_remove = device_id
            break
    if device_to_remove:
        del devices[device_to_remove]
        print(f'Device removed: {device_to_remove}')

@sio.event
async def register_device(sid, data):
    """Register device with unique ID"""
    device_id = data.get('device_id')
    if not device_id:
        await sio.emit('error', {'message': 'Device ID required'}, room=sid)
        return
    
    devices[device_id] = sid
    print(f'Device registered: {device_id}')
    await sio.emit('registered', {'device_id': device_id}, room=sid)

@sio.event
async def call_device(sid, data):
    """Initiate call to another device"""
    caller_id = None
    for device_id, device_sid in devices.items():
        if device_sid == sid:
            caller_id = device_id
            break
    
    if not caller_id:
        await sio.emit('error', {'message': 'Caller not registered'}, room=sid)
        return
    
    receiver_id = data.get('receiver_id')
    
    # Check whitelist
    if receiver_id not in DEVICE_WHITELIST.get(caller_id, []):
        await sio.emit('error', {'message': 'Not authorized to call this device'}, room=sid)
        return
    
    if receiver_id not in devices:
        await sio.emit('error', {'message': 'Receiver device not online'}, room=sid)
        return
    
    receiver_sid = devices[receiver_id]
    
    # Auto-accept if receiver is in whitelist
    await sio.emit('incoming_call', {
        'caller_id': caller_id,
        'auto_accept': True
    }, room=receiver_sid)
    
    print(f'Call initiated: {caller_id} -> {receiver_id}')

@sio.event
async def webrtc_offer(sid, data):
    """Forward WebRTC offer"""
    target_id = data.get('target_id')
    if target_id in devices:
        target_sid = devices[target_id]
        await sio.emit('webrtc_offer', {
            'offer': data.get('offer'),
            'caller_id': data.get('caller_id')
        }, room=target_sid)

@sio.event
async def webrtc_answer(sid, data):
    """Forward WebRTC answer"""
    target_id = data.get('target_id')
    if target_id in devices:
        target_sid = devices[target_id]
        await sio.emit('webrtc_answer', {
            'answer': data.get('answer')
        }, room=target_sid)

@sio.event
async def ice_candidate(sid, data):
    """Forward ICE candidates"""
    target_id = data.get('target_id')
    if target_id in devices:
        target_sid = devices[target_id]
        await sio.emit('ice_candidate', {
            'candidate': data.get('candidate')
        }, room=target_sid)

if __name__ == '__main__':
    web.run_app(app, host='192.168.0.3', port=8080)
