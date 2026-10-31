[app]
title = Architect Media Engine
package.name = mediaengine
package.domain = org.architect
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,pyjnius

# Android permissions for network and background processing
android.permissions = INTERNET, WAKE_LOCK
android.api = 33
android.minapi = 21
android.archs = armeabi-v7a, arm64-v8a
orientation = portrait
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
