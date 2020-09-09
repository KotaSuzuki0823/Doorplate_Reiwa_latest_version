'''
GUI
'''
import socket
import traceback
import sys
import queue
import ast
import threading
import json

#https://pypi.org/project/PySimpleGUI/
import PySimpleGUI as sg

import motion

#styledataの初期状態
BLANK_STYLEDATA = {'Title': "離席中", 'SubTitle': "しばらく席を外しています",\
'Background_Color': "FF000000", 'Text_Color': "FFFFFFFF", 'Token': ""}

#styledataのキュー（FIFO）
styledata_queue: "Queue[dict]" = queue.Queue()
styledata_queue.put(BLANK_STYLEDATA)

args = sys.argv

def load_android():
    """
    Bluetoothを用いてAndroidからデータの読み込み
    https://qiita.com/shippokun/items/0953160607833077163f
    :return:
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((args[1], 55555))
        print('\033[32m'+"Socket"+'\033[0m'+":Create socket "+args[1]+" 55555")
        s.listen(1)

        while True:
            print('\033[32m'+"Socket"+'\033[0m'+":Listening...")
            try:
                # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
                conn, addr = s.accept()
                print('\033[32m'+"Socket"+'\033[0m'+":Connection: "+str(addr[0]))

                # データを受け取る
                data: bytes = conn.recv(1024)
                # 先頭部分の「\x01\x16」を除いた部分で文字列型へ変換（UTF8）
                data_string: str = str(data[2:].decode())

                print('\033[32m'+"Socket"+'\033[0m'+":"+data_string)
                dicdata: dict = ast.literal_eval(data_string)

                styledata_queue.put(dicdata)

            except (socket.error, OSError) as sock_e:
                print('\033[32m'+"Socket"+'\033[0m'+":["+'\033[31m'+"Fatal"+'\033[0m'+"]%s\n" % sock_e)
                styledata_queue.put(BLANK_STYLEDATA)
                # break

            except Exception:
                traceback.print_exc()

            finally:
                conn.close()


def on_screen():
    """
    GUI表示する部分
    https://qiita.com/dario_okazaki/items/656de21cab5c81cabe59
    :return:
    """
    motion_detect = motion.MotionDetect()
    motion_thread = threading.Thread(target=motion_detect.motion)
    motion_thread.start()

    while True:
        try:
            print('\033[36m' + "getting styledate from queue..." + '\033[0m')
            styledata = styledata_queue.get()

            motion_detect.update_token(styledata.get('Token'))

            print("Setting coler theme")
            # ベースとなるテーマを指定（内容は不問）
            sg.theme('Dark2')

            background_color_code: str = '#' + styledata.get('Background_Color')[2:8]
            text_color_code: str = '#' + styledata.get('Text_Color')[2:8]

            # 背景の色を変更
            sg.theme_background_color(background_color_code)
            # 文字カラーの変更
            sg.theme_text_color(text_color_code)

            layout = [
                [sg.Text(" ", font=('ゴシック体', 60), size=(35, 1),\
                justification='center', relief=sg.RELIEF_RIDGE,\
                background_color=background_color_code)],
                [sg.Text(styledata['Title'], font=('ゴシック体', 60), size=(35, 1),\
                justification='center', relief=sg.RELIEF_RIDGE,\
                background_color=background_color_code)],
                [sg.Text(styledata['SubTitle'], font=('ゴシック体', 48), size=(45, 1),\
                justification='center', background_color=background_color_code)]
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

        except queue.Empty as queue_ex:
            print(sys.exc_info())
            print(queue_ex)
            continue

        except KeyboardInterrupt:
            sys.exit()


def main():
    """
    main関数
    """
    thread = threading.Thread(target=load_android)
    thread.start()

    on_screen()

if __name__ == "__main__":
    main()
