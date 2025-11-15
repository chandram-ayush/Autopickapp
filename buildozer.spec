[app]
title = VideoCaller
package.name = videocaller
package.domain = org.autopick

# Main entry point - CRITICAL: must specify your main file
source.main = main.py

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

# Fixed requirements - removed problematic packages for Android
requirements = python3==3.10.6,hostpython3==3.10.6,kivy==2.2.1,python-socketio==5.9.0,python-engineio==4.7.1,websocket-client==1.6.1,aiohttp==3.8.5,pillow,numpy

# Android permissions
permissions = INTERNET,CAMERA,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,ACCESS_NETWORK_STATE,WAKE_LOCK,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.permissions = android.permission.INTERNET,android.permission.CAMERA,android.permission.RECORD_AUDIO,android.permission.MODIFY_AUDIO_SETTINGS,android.permission.ACCESS_NETWORK_STATE,android.permission.WAKE_LOCK,android.permission.WRITE_EXTERNAL_STORAGE,android.permission.READ_EXTERNAL_STORAGE

# Android API settings
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.skip_update = False
android.release_artifact = apk

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Orientation
orientation = portrait
fullscreen = 0

# Features
android.features = android.hardware.camera,android.hardware.camera.autofocus

[buildozer]
log_level = 2
warn_on_root = 1
