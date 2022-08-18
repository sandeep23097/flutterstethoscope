import pickle
import struct
from threading import *
import pyaudio
import websocket
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


p = pyaudio.PyAudio()
CHUNK = 1024
Recordframes = []
stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=44100,
                        output=True,
                        frames_per_buffer=CHUNK)
data = b""
payload_size = struct.calcsize("Q")
connectState = "Playing"

def on_message(ws, message):
    global data

    while len(data) < payload_size:

        packet = message  # 4K
        # print(type(packet))
        # print(type(data))
        # packet = de.encode('utf-8')
        if not packet: break
        data += packet
    packed_msg_size = data[:payload_size]
    # print('packed_msg_size')
    # print(packed_msg_size)
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]
    # print('msg_size')
    # print(msg_size)
    while len(data) < msg_size:
        data += message
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    Recordframes.append(frame)
    # _VARS['window'].FindElement('-PROG-').Update("listening")
    stream.write(frame)
    return


def on_error(ws, error):
    global connectState
    connectState = error
    print(error)
    return


def on_close(ws, d, de):
    global connectState
    connectState = 'closed'
    print("### closed ###")
    t = Thread(target=connection)
    t.start()
    return


def on_open(ws):
    global connectState
    connectState = 'opened'
    print("opened")
    MainApp().update_txt('opended');
    # global data
    # ws.send("hi")
    # ws.send("test")

    return

class MainApp(App):
    global connectState
    my = connectState
    def build(self):
        main_layout = BoxLayout(orientation="vertical")
        h_layout = BoxLayout()
        button = Button(text=self.my,
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button.bind(on_press=self.on_press_button)
        h_layout.add_widget(button)
        main_layout.add_widget(h_layout)

        return main_layout

    def on_press_button(self, instance):

        print('You pressed the button!')
    def update_txt(self,str):
        print('hey')
        print(str)
        self.my = 'kkkk'
        self.title = self.my



def connection():
    ws = websocket.WebSocketApp("wss://fluttersocket23.herokuapp.com/", on_open=on_open, on_message=on_message,
                                on_error=on_error, on_close=on_close)
    # ws.on_open = on_open

    ws.run_forever()
    return


if __name__ == '__main__':
    t = Thread(target=connection)
    t.start()
    app = MainApp()
    app.run()