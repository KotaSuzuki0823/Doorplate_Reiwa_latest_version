'''
GUI
'''
import json
import queue
import concurrent.futures

# https://pypi.org/project/PySimpleGUI/
import PySimpleGUI as sg
import bluetooth

# style dataの初期状態
DefaultStyleData = {'color': "Dark2", 'maintext': "離席中", 'subtext': "しばらく席を外しています"}
# style dataのキュー（FIFO）
StyleDataQueue = queue.Queue()
StyleDataQueue.put(DefaultStyleData)

def loadFromAndroid():
    """
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return: json
    """
    while True:
        print("Bluetooth:Creating Bluetooth socket")
        bsocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = 5
        bsocket.bind(port)
        bsocket.listen(1)
        print("Bluetooth:listening...")

        client_socket, address = bsocket.accept()
        print("Bluetooth:Accepted connection from %s" % address)

        while True:
            try:
                # 受信するまでブロッキング
                data = client_socket.recv(1024)
                print("Bluetooth:received [%s]" % data)
                # Queueへ格納
                StyleDataQueue.put(data)

            # Bluetooth関連の例外が発生した場合に処理
            except (bluetooth.BluetoothError, bluetooth.BluetoothSocket) as bte:
                print("Bluetooth:%s\n" % bte)
                client_socket.close()
                bsocket.close()
                StyleDataQueue.put(DefaultStyleData)
                print("Bluetooth:Socket is Closed.(Disconnect) Put DefaultStyleData.")
                break

            except Exception as e:
                print("Bluetooth:[Fatal] %s\n" % e)
                client_socket.close()
                bsocket.close()
                break

            # 例外が発生しなかった場合に処理
            else:
                print("Bluetooth:No error. loop")

def onScreen():
    """
    GUI表示する部分
    https://qiita.com/dario_okazaki/items/656de21cab5c81cabe59
    :return:
    """
    while True:  # Event Loop
        std = StyleDataQueue.get(block=True)

        sg.theme(std['color'])
        layout = [
            [sg.Text(std['maintext'], font=('ゴシック体', 36), size=(30, 1), justification='center',
                     relief=sg.RELIEF_RIDGE)],
            [sg.Text(std['subtext'], font=('ゴシック体', 24), size=(30, 1), justification='center')]
        ]
        window = sg.Window('ドアプレート', layout, no_titlebar=False, location=(0, 0), default_element_size=(40, 10),
                           element_justification='c', grab_anywhere=True).Finalize()
        window.Maximize()

        event, values = window.read(timeout=30000)  # ウインドウ作成
        if event is None:
            window.close()
            break

        # Queueが空でない場合(最新の情報があるなど)はウインドウを閉じる
        if not StyleDataQueue.empty():
            window.close()
        else:
            continue

if __name__ == "__main__":
    # 並行処理にてBluetooth通信を開始
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    executor.submit(loadFromAndroid)

    # GUIの表示
    onScreen()
