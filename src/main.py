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
BlankStyledata = {'Title': "離席中", 'SubTitle': "しばらく席を外しています", 'Background_Color': "FF000000", 'Text_Color': "FFFFFFFF"}
#styledataのキュー（FIFO）
StyleDataQueue = queue.Queue()
StyleDataQueue.put({'Title': "在席中", 'SubTitle': "現在部屋にいます", 'Background_Color': "FF000000", 'Text_Color': "FFFFFFFF"})

def loadFromAndroid():
    """
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return:
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
            # 受信するまでブロッキング
            data = client_sock.recv(1024)
            print ("Bluetooth:received [%s]" % data)
            # 受信したデータを辞書型（JSON）に変換
            jsondata = json.loads(data)
            
            # Queueへ格納
            StyledataQueue.put(jsondata)

        except (json.JSONDecodeError, ValueError) as je:
            # JSON変換に関連する例外（ValueErrorはJSONDecodeErrorの親クラス）
            print ("Bluetooth:[JSON Exception]%s\n" % je)

        except (bluetooth.BluetoothError, bluetooth.BluetoothSocket) as bte:
            # Bluetoothに関連する例外
            print ("Bluetooth:%s\n" % bte)
            client_socket.close()
            bsocket.close()
            #StyleDataQueue.put(BlankStyledata)
            print ("Bluetooth:Socket is Closed.(Disconnect)")

        except Exception as e:
            # 上記以外の例外
            print ("Bluetooth:[Exception]%s\n" % e)

        except:
            # クリティカルな例外（終了させる）
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
            print ("getting styledate from queue...")
            styledata = StyleDataQueue.get()
            #json.loads(styledata)

        except Exception as e:
            print(sys.exc_info())
            print(e)
            continue
        
        print ("Setting coler theme")
        sg.theme('Dark2')
        
        Background_Color_Code = '#' + styledata['Background_Color'][2:8]
        Text_Color_Code = '#' + styledata['Text_Color'][2:8]

        # 背景の色を変更
        sg.theme_background_color(Background_Color_Code)
        # 文字カラーの変更
        sg.theme_text_color(Text_Color_Code)

        layout = [
            [sg.Text(styledata['Title'], font=('ゴシック体', 60), size=(35, 1), justification='center', relief=sg.RELIEF_RIDGE)],
            [sg.Text(styledata['SubTitle'], font=('ゴシック体', 48), size=(45, 1), justification='center')]
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