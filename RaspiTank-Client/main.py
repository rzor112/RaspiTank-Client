from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FallOutTransition, FadeTransition
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.factory import Factory
from kivy.clock import Clock
import socket, json, time

Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '600')

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

    def send(self, MESSAGE):
        try:
            if self.connected:
                self.s.send(MESSAGE)
                data = self.s.recv(self.BUFFER_SIZE)
                return json.loads(data)
            else:
                print 'You are not connected!'
                return None
        except Exception as e:
            print e
            return None


class MainScreen(Screen):
    connect_button = ObjectProperty(None)
    ping_label = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.ping, 1)

    def ping(self, *args):
        if tcp_client.connected:
            saved_time = time.time()
            data = tcp_client.send('{"command": 255, "value": 0}')
            if data and data['data']['command'] == 0xff:
                ping_time = int((time.time() - saved_time) * 1000)
                self.ping_label.text= "ping: " + str(ping_time) + "ms"

    def button_forward(self):
        if tcp_client.connected:
            tcp_client.send('{"command": 1, "value": 0}')

    def button_back(self):
        if tcp_client.connected:
            tcp_client.send('{"command": 2, "value": 0}')

    def button_left(self):
        if tcp_client.connected:
            tcp_client.send('{"command": 3, "value": 0}')

    def button_right(self):
        if tcp_client.connected:
            tcp_client.send('{"command": 4, "value": 0}')

    def button_disconnect(self):
        if tcp_client.connected:
            tcp_client.disconnect()

    def stop(self):
        if tcp_client.connected:
            tcp_client.send('{"command": 0, "value": 0}')

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