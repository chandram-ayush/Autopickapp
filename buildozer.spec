[app]
title = VideoCaller
package.name = videocaller
package.domain = org.autopick
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
source.main = main.py

# MINIMAL requirements that actually compile
requirements = python3,kivy,pillow,requests

# Permissions
android.permissions = INTERNET,CAMERA,RECORD_AUDIO,ACCESS_NETWORK_STATE,WAKE_LOCK

# Android settings
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

# Display
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
