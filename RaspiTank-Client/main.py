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

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

def tcp_send(data):
    TCP_IP = '192.168.0.115'
    TCP_PORT = 5005
    BUFFER_SIZE = 1024
    MESSAGE = data

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

class MainScreen(Screen):
    def button_1(self):
        tcp_send('on')

    def button_2(self):
        tcp_send('off')

class SecondScreen(Screen):
    pass

class Manager(ScreenManager):
    screen_main = ObjectProperty(None)
    screen_second = ObjectProperty(None)

presentation = Builder.load_file('gui.kv')
m = Manager(transition=FadeTransition())

class SimpleKivy(App):
    def build(self):
        return m

if __name__ == "__main__":
    SimpleKivy().run()