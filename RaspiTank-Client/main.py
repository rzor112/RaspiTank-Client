from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FallOutTransition, FadeTransition
from kivy.properties import ObjectProperty, NumericProperty
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import urllib
import numpy as np
import socket, json, time

Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '600')
Window.size = (1280, 600)

stream = urllib.urlopen('http://192.168.0.113:8081/')
bytes = ''

class TCP_Client():
    #settings
    TCP_IP = '192.168.0.113'
    TCP_PORT = 5005
    BUFFER_SIZE = 1024

    #status
    connected = False

    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.TCP_IP, self.TCP_PORT))
            self.connected = True
        except Exception as e:
            self.connected = False
            print e

    def disconnect(self):
        try:
            self.s.close()
            self.connected = False
        except Exception as e:
            self.connected = False
            print e

    def send(self, command, value):
        try:
            if self.connected:
                msg = {'command': int(command), 'value': int(value)}
                self.s.send(json.dumps(msg))
                data = self.s.recv(self.BUFFER_SIZE)
                data = json.loads(data)
                if data['ResponseStatus'] and data['data']['command'] == command:
                    return data['data']
                else:
                    return None
            else:
                print 'You are not connected!'
                return None
        except Exception as e:
            print e
            return None


class MainScreen(Screen):
    connect_button = ObjectProperty(None)
    ping_label = ObjectProperty(None)
    camera_box = ObjectProperty(None)
    speed_slider = ObjectProperty(None)

    key_lock = [False, False, False, False]
    disconnect_camera_texture = Image(source = 'images/off_camera.png').texture

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.ping, 1)
        Clock.schedule_interval(self.camera, 1.0/100)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        self._keyboard.bind()

    def camera(self, *args):
        if tcp_client.connected:
            global bytes
            bytes += stream.read(1024)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b+2]
                bytes = bytes[b+2:]
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                buf1 = cv2.flip(frame, 0)
                buf = buf1.tostring()
                image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.camera_box.texture = image_texture
        else:
            self.camera_box.texture = self.disconnect_camera_texture

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = Non

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'w' or keycode[1] == 'up':
            if not self.key_lock[0]:
                self.button_forward()
                self.key_lock[0] = True

        elif keycode[1] == 's' or keycode[1] == 'down':
            if not self.key_lock[1]:
                self.button_back()
                self.key_lock[1] = True

        elif keycode[1] == 'a' or keycode[1] == 'left':
            if not self.key_lock[2]:
                self.button_left()
                self.key_lock[2] = True

        elif keycode[1] == 'd' or keycode[1] == 'right':
            if not self.key_lock[3]:
                self.button_right()
                self.key_lock[3] = True

        return True

    def _on_keyboard_up(self, keyboard, keycode):
        if keycode[1] == 'w' or keycode[1] == 'up':
            self.key_lock[0] = False
            self.stop()

        elif keycode[1] == 's' or keycode[1] == 'down':
            self.key_lock[1] = False
            self.stop()

        elif keycode[1] == 'a' or keycode[1] == 'left':
            self.key_lock[2] = False
            self.stop()

        elif keycode[1] == 'd' or keycode[1] == 'right':
            self.key_lock[3] = False 
            self.stop()

        return True

    def ping(self, *args):
        if tcp_client.connected:
            saved_time = time.time()
            data = tcp_client.send(0xff, 0x00)
            if data:
                ping_time = int((time.time() - saved_time) * 1000)
                self.ping_label.text= "ping: " + str(ping_time) + "ms"

    def button_forward(self):
        if tcp_client.connected:
            tcp_client.send(0x01, 0x00)

    def button_back(self):
        if tcp_client.connected:
            tcp_client.send(0x02, 0x00)

    def button_left(self):
        if tcp_client.connected:
            tcp_client.send(0x03, 0x00)

    def button_right(self):
        if tcp_client.connected:
            tcp_client.send(0x04, 0x00)

    def button_disconnect(self):
        if tcp_client.connected:
            tcp_client.disconnect()

    def stop(self):
        if tcp_client.connected:
            tcp_client.send(0x00, 0x00)

    def set_veliocity(self, value):
        if tcp_client.connected:
            tcp_client.send(0x05, value)

    def connect(self):
        if tcp_client.connected:
            tcp_client.disconnect()
            self.connect_button.background_color = (0,1,0,1)
            self.connect_button.text = 'CONNECT'
            self.ping_label.text = ""
        else:
            tcp_client.connect()
            self.connect_button.background_color = (1,0,0,1)
            self.connect_button.text = 'DISCONNECT'
            self.speed_slider.value = tcp_client.send(0xa0, 0x00)['value']

    def settings(self):
        self.manager.current = 'screen_second'

class SecondScreen(Screen):
    def control(self):
        self.manager.current = 'screen_main'

class Manager(ScreenManager):
    screen_main = ObjectProperty(None)
    screen_second = ObjectProperty(None)

presentation = Builder.load_file('gui.kv')
m = Manager(transition=FadeTransition())

class SimpleKivy(App):
    def build(self):
        return m

tcp_client = TCP_Client()

if __name__ == "__main__":
    SimpleKivy().run()