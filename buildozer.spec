[app]
title = Architect Media Engine
package.name = mediaengine
package.domain = org.architect
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.3.0,pyjnius,libffi

# Android permissions
android.permissions = INTERNET, WAKE_LOCK
# ⚡ सर्वर पर मौजूद रेडीमेड पैकेजेस से मैच करने के लिए इसे 34 कर दिया गया है
android.api = 34
android.minapi = 21
android.archs = armeabi-v7a, arm64-v8a
orientation = portrait
fullscreen = 1

# ब्रह्मास्त्र सेटिंग्स
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.skip_update = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
