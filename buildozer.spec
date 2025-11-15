[app]
title = VideoReceiver
package.name = videoreceiver
source.main = main.py
package.domain = org.autopick
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,python-socketio,aiortc,aiohttp,opencv-python,av,numpy,websocket-client
permissions = INTERNET,CAMERA,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,ACCESS_NETWORK_STATE,WAKE_LOCK
android.permissions = INTERNET,CAMERA,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,ACCESS_NETWORK_STATE,WAKE_LOCK
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
