'''
GUI
'''
import json
import sys
import queue
from concurrent.futures import ThreadPoolExecutor

#https://pypi.org/project/PySimpleGUI/
import PySimpleGUI as sg
import bluetooth

#styledataの初期状態
BLANK_STYLEDATA = {'Title': "離席中", 'SubTitle': "しばらく席を外しています", 'Background_Color': "FF000000", 'Text_Color': "FFFFFFFF"}
#styledataのキュー（FIFO）
styledata_queue = queue.Queue()
styledata_queue.put({'Title': "在席中", 'SubTitle': "現在部屋にいます", 'Background_Color': "FF000000", 'Text_Color': "FFFFFFFF"})

def load_android():
    """
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return:
    """
    while True:
        try:
            print("Bluetooth:Socket is create.")
            bsocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            bsocket.bind(('', bluetooth.PORT_ANY))
            print("Bluetooth:Listening...")
            bsocket.listen(1)

            """
            uuid = '5E7B99D0-F404-4425-8125-98A2265B4333'
            bluetooth.advertise_service(
                bsocket, "MyServer", service_id=uuid,
                service_classes = [uuid, bluetooth.SERIAL_PORT_CLASS],
                profiles = [bluetooth.SERIAL_PORT_PROFILE],
            )
            """

            client_socket, address = bsocket.accept()
            print("Bluetooth:Accepted connection from " + address)

            # 受信するまでブロッキング
            data = client_socket.recv(1024)
            print("Bluetooth:received [%s]" % data)
            # 受信したデータを辞書型（JSON）に変換
            jsondata = json.loads(data)

            # Queueへ格納
            styledata_queue.put(jsondata)

        except (json.JSONDecodeError, ValueError) as jsone:
            # JSON変換に関連する例外（ValueErrorはJSONDecodeErrorの親クラス）
            print("Bluetooth:[JSON Exception]%s\n" % jsone)

        except (bluetooth.BluetoothError, bluetooth.BluetoothSocket) as bte:
            # Bluetoothに関連する例外
            print("Bluetooth:%s\n" % bte)
            client_socket.close()
            bsocket.close()
            #styledata_queue.put(BLANK_STYLEDATA)
            print("Bluetooth:Socket is Closed.(Disconnect)")

        except queue.Full as queue_ex:
            print(queue_ex)

        except Exception as e:
            # クリティカルな例外（終了させる）
            print("Bluetooth:[Fatal]\n")
            client_socket.close()
            bsocket.close()
            styledata_queue.put(BLANK_STYLEDATA)
            break

        else:
            print("Bluetooth:No error. loop")

def on_screen():
    """
    GUI表示する部分
    https://qiita.com/dario_okazaki/items/656de21cab5c81cabe59
    #:param styledata: Androidから送られてきたJSON形式のデータ
    :return:
    """
    while True:
        try:
            print("getting styledate from queue...")
            styledata = styledata_queue.get()
            #json.loads(styledata)

        except queue.Empty as queue_ex:
            print(sys.exc_info())
            print(queue_ex)
            continue

        print("Setting coler theme")
        sg.theme('Dark2')

        background_coler_code = '#' + styledata['Background_Color'][2:8]
        text_coler_code = '#' + styledata['Text_Color'][2:8]

        # 背景の色を変更
        sg.theme_background_color(background_coler_code)
        # 文字カラーの変更
        sg.theme_text_color(text_coler_code)

        layout = [
            [sg.Text(styledata['Title'], font=('ゴシック体', 60), size=(35, 1), justification='center', relief=sg.RELIEF_RIDGE)],
            [sg.Text(styledata['SubTitle'], font=('ゴシック体', 48), size=(45, 1), justification='center')]
        ]

        window = sg.Window('ドアプレート', layout, location=(0, 0), size=(1920, 1200), grab_anywhere=True)

        event, values = window.read(timeout=10000)  # ウインドウ作成
        if event is None:
            window.close()
            break

        # Queueが空でない場合はウインドウを閉じる
        if not styledata_queue.empty():
            window.close()
        else:
            continue

if __name__ == "__main__":
    with ThreadPoolExecutor(1) as executor:
        FUTURE = executor.submit(load_android)

    # on_screen()
