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

# ⚡ सीक्रेट पैच: इसे जबरदस्ती सही NDK का पाथ और वर्जन बताना
android.ndk = 25.2.9519653
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.skip_update = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
