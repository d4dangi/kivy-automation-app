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

class ScreenWidget(BoxLayout):
    """4x10 ग्रिड की हर एक छोटी स्क्रीन का विजेट"""
    def __init__(self, screen_id, **kwargs):
        super().__init__(orientation='vertical', padding=2, **kwargs)
        self.screen_id = screen_id
        
        # टॉप स्टेटस रो (LED + ID)
        status_row = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        self.lbl_id = Label(text=f"SCR-{screen_id}", font_size='10sp')
        status_row.add_widget(self.lbl_id)
        
        # लाइव LED ड्रा करना
        self.led_box = BoxLayout(size_hint_x=0.3)
        with self.led_box.canvas:
            self.led_color = Color(1, 0, 0, 1) # डिफ़ॉल्ट लाल 🔴
            self.led_shape = Ellipse(size=(12, 12))
        self.led_box.bind(pos=self.update_led_pos, size=self.update_led_pos)
        status_row.add_widget(self.led_box)
        
        self.add_widget(status_row)
        
        # मिनी टर्मिनल लॉग (वेबव्यू लोड स्टेटस दिखाने के लिए)
        self.lbl_log = Label(text="[OFFLINE]", font_size='9sp', color=(0.7, 0.7, 0.7, 1))
        self.add_widget(self.lbl_log)

    def update_led_pos(self, *args):
        self.led_shape.pos = (self.led_box.x + self.led_box.width/2 - 6, self.led_box.y + self.led_box.height/2 - 6)

    def set_status(self, state, log_text=""):
        """एलईडी का रंग बदलने का फंक्शन"""
        def update_ui(dt):
            self.lbl_log.text = log_text[:15]
            if state == "red":
                self.led_color.rgba = (1, 0, 0, 1) 🔴
            elif state == "yellow":
                self.led_color.rgba = (1, 1, 0, 1) 🟡
            elif state == "green":
                self.led_color.rgba = (0, 1, 0, 1) 🟢
        Clock.schedule_once(update_ui)

class ArchitectMediaEngine(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_simulating = False
        self.screens = {}
        self.master_links = []

    def build(self):
        # मुख्य लेआउट (वर्टिकल)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # ऊपर का सेक्शन (BOX 1 और BOX 2 को हॉरिजॉन्टल रखने के लिए)
        top_section = BoxLayout(orientation='horizontal', size_hint_y=0.35, spacing=10)
        
        # BOX 1: इनपुट बॉक्स
        box1 = BoxLayout(orientation='vertical', spacing=5)
        box1.add_widget(Label(text="📥 BOX 1: Paste New Links", size_hint_y=0.2))
        self.txt_input = TextInput(hint_text="यहाँ लिंक्स डालें (One per line)...", multiline=True)
        box1.add_widget(self.txt_input)
        top_section.add_widget(box1)
        
        # BOX 2: लाइव प्रोग्रेस मॉनिटर
        box2 = BoxLayout(orientation='vertical', spacing=5)
        box2.add_widget(Label(text="📊 BOX 2: Simulation Monitor", size_hint_y=0.2))
        self.scroll_monitor = ScrollView()
        self.lbl_monitor = TextInput(text="Link Simulation Stats Will Appear Here...\n", readonly=True, background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1))
        self.scroll_monitor.add_widget(self.lbl_monitor)
        box2.add_widget(self.scroll_monitor)
        top_section.add_widget(box2)
        
        main_layout.add_widget(top_section)
        
        # BOX 3: 4x10 स्क्रीन मैट्रिक्स (ग्रिड लेआउट)
        grid_container = BoxLayout(orientation='vertical', size_hint_y=0.55)
        grid_container.add_widget(Label(text="📱 BOX 3: 4x10 Live Matrix Monitor", size_hint_y=0.1))
        
        matrix_grid = GridLayout(cols=4, spacing=5, padding=5)
        for i in range(1, 41):
            scr = ScreenWidget(screen_id=i)
            matrix_grid.add_widget(scr)
            self.screens[i] = scr
            
        grid_container.add_widget(matrix_grid)
        main_layout.add_widget(grid_container)
        
        # कंट्रोल बॉक्स (3 बटन्स)
        control_box = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        btn_play = Button(text="▶ PLAY", background_color=(0, 0.8, 0, 1))
        btn_play.bind(on_press=self.start_simulation)
        btn_complete = Button(text="✔ COMPLETE", background_color=(0.8, 0.8, 0, 1))
        btn_quit = Button(text="❌ QUIT", background_color=(0.8, 0, 0, 1))
        
        control_box.add_widget(btn_play)
        control_box.add_widget(btn_complete)
        control_box.add_widget(btn_quit)
        main_layout.add_widget(control_box)
        
        return main_layout

    def start_simulation(self, instance):
        if not self.is_simulating:
            self.master_links = [line.strip() for line in self.txt_input.text.split('\n') if line.strip()]
            if not self.master_links:
                self.lbl_monitor.text += "[SYSTEM] Error: No links found in BOX 1!\n"
                return
            
            self.is_simulating = True
            self.lbl_monitor.text += f"[SYSTEM] Simulation fired up for {len(self.master_links)} links...\n"
            
            # 40 स्क्रीन्स को एक-एक करके डिले के साथ इनिशियलाइज करना (Sequential Startup)
            threading.Thread(target=self.sequential_startup_engine, daemon=True).start()

    def sequential_startup_engine(self):
        for scr_id in range(1, 41):
            if not self.is_simulating: break
            # 1. स्क्रीन को पीला करना 🟡 (IP/Fingerprint Allocation Stage)
            self.screens[scr_id].set_status("yellow", "Allocating IP...")
            time.sleep(0.5) # आपके निर्देशानुसार ऐप एक-एक करके सेटअप करेगी
            
            # 2. स्क्रीन वर्कर थ्रेड लॉन्च करना
            threading.Thread(target=self.individual_screen_worker, args=(scr_id,), daemon=True).start()

    def individual_screen_worker(self, scr_id):
        while self.is_simulating:
            # शफल लिस्ट जनरेट करना (हर राउंड की शुरुआत में)
            shuffled_list = list(self.master_links)
            random.shuffle(shuffled_list)
            
            # 3. स्क्रीन को हरा करना 🟢 (Player Live & Working Stage)
            fake_ip = f"{random.randint(100,254)}.{random.randint(10,99)}.{random.randint(1,9)]}"
            self.screens[scr_id].set_status("green", f"IP: {fake_ip}")
            
            for index, link in enumerate(shuffled_list):
                if not self.is_simulating: break
                
                # BOX 2 लाइव अपडेट लॉजिक
                def update_stats(dt, s_id=scr_id, l=link):
                    self.lbl_monitor.text += f"[SCR {s_id}] Playing: {l[:25]}...\n"
                Clock.schedule_once(update_stats)
                
                # सिम्युलेटेड मीडिया प्ले टाइमर (बताए गए समय तक प्ले होना)
                time.sleep(8) 
                
            # राउंड कम्प्लीट होने पर रिफ्रेश स्टेज (वापस पीला 🟡 होकर नई IP लेना)
            if self.is_simulating:
                self.screens[scr_id].set_status("yellow", "Rotating IP...")
                time.sleep(2) # आईपी रोटेशन डिले

if __name__ == '__main__':
    ArchitectMediaEngine().run()
