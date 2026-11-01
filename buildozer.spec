[app]
title = Architect Media Engine
package.name = mediaengine
package.domain = org.architect
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
# ⚡ हमने मैन्युअल libffi हटा दिया है ताकि Kivy खुद को ऑटो-सिंक कर सके
requirements = python3,kivy,pyjnius

# Android permissions
android.permissions = INTERNET, WAKE_LOCK
android.api = 34
android.minapi = 21
android.archs = armeabi-v7a, arm64-v8a
orientation = portrait
fullscreen = 1

# ब्रह्मास्त्र सेटिंग्स (सिस्टम SDK को फोर्स करना)
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.skip_update = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
