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

# ⚡ सीक्रेट ब्रह्मास्त्र लाइन्स: यह डाउनलोडिंग को रोककर सीधे सिस्टम SDK का रास्ता दिखाता है
android.skip_update = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
