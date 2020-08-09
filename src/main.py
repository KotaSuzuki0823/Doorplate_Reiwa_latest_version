'''
GUI
'''
import json
import sys
import multiprocessing
import queue

#https://pypi.org/project/PySimpleGUI/
import PySimpleGUI as sg
import bluetooth

#styledataの初期状態
BlankStyledata = {'color': "Dark2", 'maintext': "離席中", 'subtext': "しばらく席を外しています"}
#styledataのキュー（FIFO）
StyledataQueue = queue.Queue()
StyledataQueue.put(BlankStyledata)

def loadFromAndroid():
    '''
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return: json
    '''
    while(True):
        bsocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = 5
        bsocket.bind(port)
        bsocket.listen(1)

        client_socket,address = bsocket.accept()
        print ("Accepted connection from " + address)

        try:
            data = client_sock.recv(1024)#受信するまでブロッキング
            print ("received [%s]" % data)
            #Queueへ格納
            StyledataQueue.put(data)

        except Exception as e:
            print ("Exception:%s\n" % e)

        except (bluetooth.BluetoothError, bluetooth.BluetoothSocket) as bte:
            print ("Bluetooth:%s\n" % bte)
            client_socket.close()
            bsocket.close()
            StyledataQueue.put(BlankStyledata)
            print ("Socket is Closed.(Disconnect) Put BlankStyledata.")

        except:
            print ("Fatal:%s\n" % e)
            client_socket.close()
            bsocket.close()
            StyledataQueue.put(BlankStyledata)
            break

        else:
            print ("No error. loop")

def onScreen():
    '''
    GUI表示する部分
    https://qiita.com/dario_okazaki/items/656de21cab5c81cabe59
    #:param styledata: Androidから送られてきたJSON形式のデータ
    :return:
    '''
    while(True):
        try:
            styledata = StyledataQueue.get()
            json.loads(styledata)

        except Exception as e:
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

if __name__ == "__main__":
    pass