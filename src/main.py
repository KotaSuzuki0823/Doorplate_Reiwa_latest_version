'''
GUI
'''
import socket
import traceback
import sys
import queue
import ast
from concurrent.futures import ThreadPoolExecutor

#https://pypi.org/project/PySimpleGUI/
import PySimpleGUI as sg
# import bluetooth

#styledataの初期状態
BLANK_STYLEDATA = {'Title': "離席中", 'SubTitle': "しばらく席を外しています", 'Background_Color': "FF000000", 'Text_Color': "FFFFFFFF", 'Token': ""}
#styledataのキュー（FIFO）
styledata_queue = queue.Queue()
styledata_queue.put(BLANK_STYLEDATA)

args = sys.argv

def load_android():
    """
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return:
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # s.bind((args[1], 55555))
        s.bind(("192.168.100.51", 55555))
        print("Socket:Create socket"+args[1]+" 55555")

        s.listen(1)

        while True:
            try:
                print("Socket:Listening...")
                # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
                conn, addr = s.accept()
                print("Soket:Connection: "+str(addr[0]))
            
                # データを受け取る
                data = conn.recv(1024)
                print("Socket:"+str(data.decode('utf-8')))
                dicdata = ast.literal_eval("{" + str(data) + "}")
                styledata_queue.put(dicdata)

            except (ValueError, queue.Full) as jsone:
                print("Socket:[JSON Exception]%s\n" % jsone)

            except socket.error as e:
                # クリティカルな例外（終了させる）
                print("Socket:[Fatal]\n")
                styledata_queue.put(BLANK_STYLEDATA)
                # break

            except Exception as ee:
                traceback.print_exc()

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
    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.submit(load_android)

    on_screen()
        
