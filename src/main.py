'''
GUI
'''
import json
import sys

import PySimpleGUI as sg
import bluetooth

import bt

def loadFromAndroid():
    '''
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return: json
    '''

    while 1:
        bsocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = 5
        bsocket.bind(port)
        bsocket.listen(1)

        client_socket,address = bsocket.accept()
        print ("Accepted connection from " + address)

        try:
            data = client_sock.recv(1024)
            print ("received [%s]" % data)
        except KeyboardInterrupt:
            client_socket.close()
            server_socket.close()
            break
        except:
            print ("Bluetooth error\n")
            client_socket.close()
            server_socket.close()
            break

def onScreen(styledata):
    '''
    GUI表示する部分
    https://qiita.com/dario_okazaki/items/656de21cab5c81cabe59
    :param styledata: Androidから送られてきたJSON形式のデータ
    :return:
    '''
    while(True):
        try:
            json.loads(styledata)
        except json.JSONDecodeError as e:
            print(sys.exc_info())
            print(e)
            continue

        sg.theme(styledata['color'])

        layout = [
            [sg.Text(styledata['maintext'])],
            [],
            [sg.Text(styledata['subtext'])]
        ]
        window = sg.Window('ドアプレート', layout)

def storeJSON():
    pass

if __name__ == "__main__":
    pass