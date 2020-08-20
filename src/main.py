'''
GUI
'''
import json
import sys
import multiprocessing
import queue
from concurrent.futures import ThreadPoolExecutor

#https://pypi.org/project/PySimpleGUI/
import PySimpleGUI as sg
import bluetooth

#styledataの初期状態
BlankStyledata = {'color': "Dark2", 'maintext': "離席中", 'subtext': "しばらく席を外しています"}
#styledataのキュー（FIFO）
StyleDataQueue = queue.Queue()
StyleDataQueue.put({'color': "Dark2", 'maintext': "在室中", 'subtext': "現在部屋にいます．"})

def loadFromAndroid():
    """
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return: json
    """
    while True:
        print ("Bluetooth:Socket is create.")
        bsocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = 5
        bsocket.bind(port)
        print ("Bluetooth:Listening...")
        bsocket.listen(1)

        client_socket,address = bsocket.accept()
        print ("Bluetooth:Accepted connection from " + address)

        try:
            data = client_sock.recv(1024)#受信するまでブロッキング
            print ("Bluetooth:received [%s]" % data)
            #Queueへ格納
            StyledataQueue.put(data)

        except Exception as e:
            print ("Bluetooth:[Exception]%s\n" % e)

        except (bluetooth.BluetoothError, bluetooth.BluetoothSocket) as bte:
            print ("Bluetooth:%s\n" % bte)
            client_socket.close()
            bsocket.close()
            StyleDataQueue.put(BlankStyledata)
            print ("Bluetooth:Socket is Closed.(Disconnect) Put BlankStyledata.(bluetooth exception)")

        except:
            print ("Bluetooth:[Fatal]\n")
            client_socket.close()
            bsocket.close()
            StyleDataQueue.put(BlankStyledata)
            break

        else:
            print ("Bluetooth:No error. loop")

def onScreen():
    """
    GUI表示する部分
    https://qiita.com/dario_okazaki/items/656de21cab5c81cabe59
    #:param styledata: Androidから送られてきたJSON形式のデータ
    :return:
    """
    while True:
        try:
            styledata = StyleDataQueue.get()
            json.loads(styledata)

        except Exception as e:
            print(sys.exc_info())
            print(e)
            continue

        sg.theme(styledata['color'])

        layout = [
            [sg.Text(styledata['maintext'], font=('ゴシック体', 60), size=(35, 1), justification='center', relief=sg.RELIEF_RIDGE)],
            [sg.Text(styledata['subtext'], font=('ゴシック体', 48), size=(45, 1), justification='center')]
        ]
        window = sg.Window('ドアプレート', layout, location=(0,0), size=(1920,1200), grab_anywhere=True)

        event, values = window.read(timeout=10000)  # ウインドウ作成
        if event is None:
            window.close()
            break

        # Queueが空でない場合はウインドウを閉じる
        if not StyleDataQueue.empty():
            window.close()
        else:
            continue

if __name__ == "__main__":
    with ThreadPoolExecutor(1) as executor:
        future = executor.submit(loadFromAndroid)
    
    onScreen()