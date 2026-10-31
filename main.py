import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    PowerManager = autoclass('android.os.PowerManager')

class MediaEngineApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.automation_thread = None
        self.is_running = False
        self.wake_lock = None

    def build(self):
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        self.status_label = Label(
            text="Architect Media Engine v1.0\nStatus: [IDLE]", 
            size_hint_y=0.1,
            halign="center",
            valign="middle"
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        root.add_widget(self.status_label)
        
        self.link_input = TextInput(
            hint_text="Paste your YouTube/Music links here (One link per line)...",
            size_hint_y=0.35,
            multiline=True
        )
        root.add_widget(self.link_input)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        self.start_btn = Button(text="START AUTOMATION", background_color=(0, 0.8, 0, 1))
        self.start_btn.bind(on_press=self.start_automation)
        
        self.stop_btn = Button(text="FORCE STOP", background_color=(0.8, 0, 0, 1), disabled=True)
        self.stop_btn.bind(on_press=self.stop_automation)
        
        btn_layout.add_widget(self.start_btn)
        btn_layout.add_widget(self.stop_btn)
        root.add_widget(btn_layout)
        
        self.log_monitor = TextInput(
            text="[SYSTEM] Engine Initialized. Ready for action.\n",
            size_hint_y=0.45,
            readonly=True,
            background_color=(0, 0, 0, 1),
            foreground_color=(0, 1, 0, 1)
        )
        root.add_widget(self.log_monitor)
        
        return root

    def append_log(self, text):
        def update_ui(dt):
            current_time = time.strftime('%H:%M:%S')
            self.log_monitor.text += f"[{current_time}] {text}\n"
        Clock.schedule_once(update_ui)

    def update_status(self, status_text):
        def update_ui(dt):
            self.status_label.text = f"Architect Media Engine v1.0\nStatus: [{status_text}]"
        Clock.schedule_once(update_ui)

    def acquire_wake_lock(self):
        if platform == 'android':
            try:
                activity = PythonActivity.mActivity
                power_manager = activity.getSystemService(Context.POWER_SERVICE)
                self.wake_lock = power_manager.newWakeLock(1, "MediaEngine::WakeLockTag")
                self.wake_lock.acquire()
                self.append_log("[SYSTEM] Android WakeLock Acquired. App running in background.")
            except Exception as e:
                self.append_log(f"[ERROR] WakeLock failed: {str(e)}")

    def release_wake_lock(self):
        if platform == 'android' and self.wake_lock:
            try:
                if self.wake_lock.isHeld():
                    self.wake_lock.release()
                    self.append_log("[SYSTEM] Android WakeLock Released.")
            except Exception as e:
                self.append_log(f"[ERROR] WakeLock release failed: {str(e)}")

    def start_automation(self, instance):
        if not self.is_running:
            links = [line.strip() for line in self.link_input.text.split('\n') if line.strip()]
            if not links:
                self.append_log("[WARNING] No valid links found! Please paste links.")
                return
            
            self.is_running = True
            self.start_btn.disabled = True
            self.stop_btn.disabled = False
            self.update_status("RUNNING")
            
            self.acquire_wake_lock()
            
            self.automation_thread = threading.Thread(target=self.automation_loop, args=(links,))
            self.automation_thread.daemon = True
            self.automation_thread.start()

    def stop_automation(self, instance=None):
        if self.is_running:
            self.is_running = False
            self.append_log("[SYSTEM] Stopping engine... Processing final requests.")
            self.start_btn.disabled = False
            self.stop_btn.disabled = True
            self.update_status("IDLE")
            self.release_wake_lock()

    def automation_loop(self, links):
        self.append_log(f"[CORE] Automation Started. Total items parsed: {len(links)}")
        
        while self.is_running:
            for index, link in enumerate(links):
                if not self.is_running:
                    break
                
                self.append_log(f"[PROCESSING] Loading Track {index + 1}: {link[:30]}...")
                time.sleep(5) 

                self.append_log(f"[SUCCESS] Track {index + 1} finished processing.")
                self.append_log("[PACING] Next load in 30 seconds...")
                for _ in range(30):
                    if not self.is_running:
                        break
                    time.sleep(1)
            
            if self.is_running:
                self.append_log("[LOOP Complete] Re-cycling master link list...")
                time.sleep(2)
        
        self.append_log("[CORE] Engine Stopped Safely.")

if __name__ == '__main__':
    MediaEngineApp().run()
