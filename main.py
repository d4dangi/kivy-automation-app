import threading
import time
import random
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse
from kivy.utils import platform

# एंड्रॉइड स्पेसिफिक जावा ब्रिज (WakeLock के लिए)
if platform == 'android':
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    PowerManager = autoclass('android.os.PowerManager')

class ScreenWidget(BoxLayout):
    """बॉक्स 3 की 4x10 मैट्रिक्स की हर एक मिनी स्क्रीन का यूआई विजेट"""
    def __init__(self, screen_id, **kwargs):
        super().__init__(orientation='vertical', padding=2, spacing=2, **kwargs)
        self.screen_id = screen_id
        
        # स्टेटस लाइन (LED इंडिकेटर बत्ती + स्क्रीन आईडी)
        status_row = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        self.lbl_id = Label(text=f"SCR-{screen_id:02d}", font_size='11sp', bold=True)
        status_row.add_widget(self.lbl_id)
        
        # एलईडी बत्ती ड्रॉ करना
        self.led_box = BoxLayout(size_hint_x=0.4)
        with self.led_box.canvas:
            self.led_color = Color(1, 0, 0, 1) # डिफ़ॉल्ट: लाल 🔴 (नो कनेक्शन)
            self.led_shape = Ellipse(size=(14, 12))
        self.led_box.bind(pos=self.update_led_geometry, size=self.update_led_geometry)
        status_row.add_widget(self.led_box)
        self.add_widget(status_row)
        
        # लाइव प्रोग्रेस/ट्रैक नाम दिखाने के लिए छोटा लेबल
        self.lbl_status = Label(text="OFFLINE", font_size='9sp', color=(0.6, 0.6, 0.6, 1))
        self.add_widget(self.lbl_status)

    def update_led_geometry(self, *args):
        self.led_shape.pos = (self.led_box.x + self.led_box.width/2 - 7, self.led_box.y + self.led_box.height/2 - 6)

    def change_indicator_light(self, color_name, text_info=""):
        """थ्रेड-सुरक्षित तरीके से एलईडी इंडिकेटर बत्ती का रंग बदलना"""
        def update_ui(dt):
            self.lbl_status.text = text_info[:18]
            if color_name == "red":
                self.led_color.rgba = (1, 0, 0, 1)      # 🔴 लाल: डिस्कनेक्टेड
            elif color_name == "yellow":
                self.led_color.rgba = (1, 1, 0, 1)   # 🟡 पीला: तैयार (आईपी एलोकेटेड)
            elif color_name == "green":
                self.led_color.rgba = (0, 1, 0, 1)     # 🟢 हरा: मीडिया एक्टिवली प्लेइंग
        Clock.schedule_once(update_ui)

class ArchitectMediaEngine(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_running = False
        self.matrix_screens = {}
        self.links_database = {} # {url: [total_played_count, current_screen_owner]}
        self.wake_lock = None

    def build(self):
        # मेन पैरेंट लेआउट
        main_view = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # 📥 टॉप सेक्शन (BOX 1 और BOX 2 को अगल-बगल सेट करने के लिए)
        top_split_panel = BoxLayout(orientation='horizontal', size_hint_y=0.35, spacing=10)
        
        # BOX 1: इनपुट बॉक्स इंजन
        box1_layout = BoxLayout(orientation='vertical', spacing=2)
        box1_layout.add_widget(Label(text="📥 BOX 1: Master Link Input Engine", size_hint_y=0.15, bold=True))
        self.txt_links_input = TextInput(
            hint_text="यहाँ अपने यूट्यूब लिंक्स पेस्ट करें (Shorts, Music, Videos - हर लाइन में एक लिंक)...", 
            multiline=True,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1)
        )
        box1_layout.add_widget(self.txt_links_input)
        top_split_panel.add_widget(box1_layout)
        
        # BOX 2: लाइव सिमुलेशन प्रोग्रेस मॉनिटर (स्क्रॉलेबल)
        box2_layout = BoxLayout(orientation='vertical', spacing=2)
        box2_layout.add_widget(Label(text="📊 BOX 2: Real-Time Loop Monitor", size_hint_y=0.15, bold=True))
        self.txt_monitor_display = TextInput(
            text="App Ready. Add links in BOX 1 and press PLAY.\n", 
            readonly=True, 
            background_color=(0.05, 0.05, 0.05, 1), 
            foreground_color=(0, 1, 0, 1) # क्लासिक ग्रीन कंसोल लुक 📟
        )
        box2_layout.add_widget(self.txt_monitor_display)
        top_split_panel.add_widget(box2_layout)
        
        main_view.add_widget(top_split_panel)
        
        # 📱 BOX 3: 4x10 लाइव स्क्रीन मैट्रिक्स मॉनिटर
        box3_layout = BoxLayout(orientation='vertical', size_hint_y=0.53, spacing=2)
        box3_layout.add_widget(Label(text="📱 BOX 3: 4x10 Live Matrix Process Panel (40 Virtual Devices)", size_hint_y=0.08, bold=True))
        
        grid_matrix = GridLayout(cols=4, spacing=4, padding=2)
        for s_id in range(1, 41):
            screen_box = ScreenWidget(screen_id=s_id)
            grid_matrix.add_widget(screen_box)
            self.matrix_screens[s_id] = screen_box
            
        box3_layout.add_widget(grid_matrix)
        main_view.add_widget(box3_layout)
        
        # ⚙ CONTROL BOX: कंट्रोल पैनल बटन्स एंकर
        control_panel = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        self.btn_play = Button(text="▶ PLAY SIMULATION", background_color=(0, 0.7, 0, 1), font_size='16sp', bold=True)
        self.btn_play.bind(on_press=self.fire_automation_engine)
        
        self.btn_complete = Button(text="✔ COMPLETE ROUND", background_color=(0.7, 0.6, 0, 1), font_size='16sp', bold=True)
        
        self.btn_quit = Button(text="❌ QUIT ENGINE", background_color=(0.7, 0, 0, 1), font_size='16sp', bold=True)
        self.btn_quit.bind(on_press=self.kill_all_processes)
        
        control_panel.add_widget(self.btn_play)
        control_panel.add_widget(self.btn_complete)
        control_panel.add_widget(self.btn_quit)
        main_view.add_widget(control_panel)
        
        return main_view

    def acquire_android_wakclock(self):
        if platform == 'android':
            try:
                activity = PythonActivity.mActivity
                power_manager = activity.getSystemService(Context.POWER_SERVICE)
                self.wake_lock = power_manager.newWakeLock(1, "MediaEngine::SecureWakeLock")
                self.wake_lock.acquire()
                self.push_monitor_log("[SYSTEM] WakeLock Secured. Phone CPU will stay alive 24/7.")
            except Exception as e:
                self.push_monitor_log(f"[ERROR] WakeLock failure: {str(e)}")

    def push_monitor_log(self, log_msg):
        def update_text(dt):
            timestamp = time.strftime('%H:%M:%S')
            self.txt_monitor_display.text += f"[{timestamp}] {log_msg}\n"
        Clock.schedule_once(update_text)

    def refresh_box2_stats_dashboard(self):
        """बॉक्स 2 के डैशबोर्ड को रिफ्रेश करना (URLs | प्रोग्रेस | लूप काउंट)"""
        def update_dashboard(dt):
            dashboard_text = "--- BOX 2: ACTIVE LINKS DASHBOARD ---\n"
            for url, stats in self.links_database.items():
                owner = f"SCR-{stats[1]:02d}" if stats[1] else "IDLE"
                dashboard_text += f"[{owner}] {url[:35]}... | Loops Done: {stats[0]}\n"
            self.txt_monitor_display.text = dashboard_text
        Clock.schedule_once(update_dashboard)

    def fire_automation_engine(self, instance):
        if not self.is_running:
            raw_lines = self.txt_links_input.text.split('\n')
            parsed_urls = [line.strip() for line in raw_lines if line.strip()]
            
            if not parsed_urls:
                self.push_monitor_log("[WARNING] No valid links found in BOX 1!")
                return
            
            self.is_running = True
            self.btn_play.disabled = True
            
            # डेटाबेस इनिशियलाइज करना
            for url in parsed_urls:
                self.links_database[url] = [0, None] # [Count, Screen_ID]
                
            self.acquire_android_wakclock()
            self.push_monitor_log(f"[CORE] Automation Master Loop Fired. Total Targets: {len(parsed_urls)}")
            
            # 40 स्क्रीन्स को क्रमिक (Sequential Setup) रूप से शुरू करने के लिए मास्टर थ्रेड
            threading.Thread(target=self.sequential_matrix_initializer, daemon=True).start()

    def sequential_matrix_initializer(self):
        """आपके निर्देशानुसार, ऐप 40 अलग-अलग स्क्रीन्स को एक-एक करके नेटवर्क आवंटित करेगी"""
        for scr_id in range(1, 41):
            if not self.is_running: break
            
            # 1. बत्ती पीली करना 🟡 (Proxy/Fingerprint Allocation Stage)
            self.matrix_screens[scr_id].change_indicator_light("yellow", "Allocating Tor IP...")
            time.sleep(0.4) # थ्रेड क्रिएशन डिले ताकि पुराना रैम हैंग न हो
            
            # 2. इस विशिष्ट स्क्रीन के लिए स्वतंत्र थ्रेड वर्कर शुरू करना
            threading.Thread(target=self.individual_screen_runtime_worker, args=(scr_id,), daemon=True).start()

    def individual_screen_runtime_worker(self, scr_id):
        """यह थ्रेड 40 स्क्रीन्स में से प्रत्येक के लिए स्वतंत्र रूप से बैकग्राउंड में लूप चलाएगा"""
        while self.is_running:
            # हर नए राउंड की शुरुआत में शफ़ल लिस्ट तैयार करना
            local_shuffled_list = list(self.links_database.keys())
            random.shuffle(local_shuffled_list)
            
            # बत्ती हरी करना 🟢 (WebView Active Layer)
            # यहाँ एंड्रॉइड का कस्टमाइज्ड जावा स्क्रिप्ट और हेडलेस वेबव्यू टनल इंजेक्ट होगा
            fake_ip = f"127.0.0.1:90{scr_id:02d}" # सिम्युलेटेड टॉर लोकल पोर्ट टनल
            self.matrix_screens[scr_id].change_indicator_light("green", f"Proxy: {fake_ip}")
            
            for url in local_shuffled_list:
                if not self.is_running: break
                
                # इस URL का मालिकाना हक इस स्क्रीन को देना (डैशबोर्ड अपडेट के लिए)
