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
import socket 

Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '600')

class TCP_Client():
    #settings
    TCP_IP = '192.168.0.111'
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
            else:
                print 'You are not connected!'
        except Exception as e:
            print e

class MainScreen(Screen):
    def button_forward(self):
        tcp_client.send('{"command": 1, "value": 0}')

    def button_back(self):
        tcp_client.send('{"command": 4, "value": 0}')

    def button_left(self):
        tcp_client.send('{"command": 3, "value": 0}')

    def button_right(self):
        tcp_client.send('{"command": 2, "value": 0}')

    def button_disconnect(self):
        tcp_client.disconnect()

    def stop(self):
        tcp_client.send('{"command": 0, "value": 0}')

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
tcp_client.connect()

if __name__ == "__main__":
    SimpleKivy().run()