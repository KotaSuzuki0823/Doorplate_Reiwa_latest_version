'''
GUI
'''
import socket
import json
import sys
import queue
from concurrent.futures import ThreadPoolExecutor

#https://pypi.org/project/PySimpleGUI/
import PySimpleGUI as sg
# import bluetooth

#styledataの初期状態
BLANK_STYLEDATA = {'Title': "離席中", 'SubTitle': "しばらく席を外しています", 'Background_Color': "FF000000", 'Text_Color': "FFFFFFFF", 'Token': ""}
#styledataのキュー（FIFO）
styledata_queue = queue.Queue()
 tyledata_queue.put({'Title': "離席中", 'SubTitle': "しばらく席を外しています", 'Background_Color': "FF000000", 'Text_Color': "FFFFFFFF", 'Token': ""})

args = sys.argv

def load_android():
    """
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return:
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((args[1], 55555))
        print("Socket:Create socket"+args[1]+" 55555")

        s.listen(1)
        print("Socket:Listening...")

        while True:
            # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
            conn, addr = s.accept()
            print("Socket:accept " + addr)
            try:
                # データを受け取る
                data = conn.recv(1024)
                print("Socket:"+data)
                jsondata = json.loads(data)
                styledata_queue.put(jsondata)

            except (json.JSONDecodeError, ValueError, queue.Full) as jsone:
                # JSON変換に関連する例外（ValueErrorはJSONDecodeErrorの親クラス）
                print("Socket:[JSON Exception]%s\n" % jsone)

            except socket.error as e:
                # クリティカルな例外（終了させる）
                print("Socket:[Fatal]\n")
                styledata_queue.put(BLANK_STYLEDATA)
                break

            finally:
                conn.close()


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
            [sg.Text(styledata['Title'], font=('ゴシック体', 60), size=(35, 1),\
            justification='center', relief=sg.RELIEF_RIDGE)],
            [sg.Text(styledata['SubTitle'], font=('ゴシック体', 48), size=(45, 1),\
            justification='center')]
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
    try:
        with ThreadPoolExecutor(1) as executor:
            FUTURE = executor.submit(load_android)

        on_screen()
    except KeyboardInterrupt:
        print(KeyboardInterrupt)
        sys.exit(1)
