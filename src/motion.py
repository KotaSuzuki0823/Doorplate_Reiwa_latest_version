"""
ラズパイカメラで動体検知し，Android端末に通知
参考：https://dream-soft.mydns.jp/blog/developper/smarthome/2020/02/678/#toc6
"""

import time
import datetime
import subprocess
import json
import os
import sys
import requests
import cv2

# ホームディレクトリのパス
HOME = os.environ['HOME']
# 画像の格納パス
PICK_PATH = HOME + '/camera/picts'

# Push通知のURL
URL = 'https://fcm.googleapis.com/fcm/send'

# サーバ通知のインターバル(秒)
INTERVAL = 30

# 動体検知の精度
DETECTSIZE = 1000

# プッシュ通知の認証キー
AUTHORIZATION_KEY = 'key=AAAAlNSzCwE:APA91bHCIcrJeRbN13m2QEY5pXjgzwpQ_q5L6qlcdBk1NJQFx2ffGxja9EHrg62Zd_sNm_r6C6HIuRKkNjygo0WhuHuYc7mGSwFGBGXiR44G6S80gKMtr3TtwnFbh4eIepOMRT8nHn7c'


def makepicpathdir(path):
    """
    撮影した写真を格納するディレクトリを作成する関数
    :param path: 保存先のパス
    :return:
    """
    try:
        os.makedirs(PICK_PATH)
        print('Created the Directory(' + path + ') ')
    except FileExistsError:
        return


def get_photo(dirpath):
    """
    ラズパイカメラで写真を撮影
    :return:　String型　撮影した画像のパス
    """
    nowstr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    photopath = dirpath + "/" + nowstr + ".jpg"
    cmd = ["raspistill", "-t", "2000", "-o", photopath]

    try:
        print("Run raspistill...")
        subprocess.check_call(cmd)

    except subprocess.CalledProcessError as ex:
        print("subprocess.check_call() failed:" + ex)
        sys.exit(1)

    return photopath


def move_detect(img):
    """
    最新の写真と1つ前の写真を比較して，差分から動体検知をする
    :parm:img cv2のImage型変数 最新の写真
    :return:　bool型　検知結果
    """
    global bef_image

    # 入力画像をグレースケールに変換
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 前画像がない場合、現画像を保存し終了
    if bef_image is None:
        bef_image = gray_image.copy().astype("float")
        print('Before image is not found. (bef_image is None) ')
        return False

    # 前画像との差分を取得する
    cv2.accumulateWeighted(gray_image, bef_image, 0.00001)
    delta = cv2.absdiff(gray_image, cv2.convertScaleAbs(bef_image))
    thresh = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]
    image, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 画像内の最も大きな差分を求める
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if max_area < area:
            max_area = area

    # 現在時間を取得
    now_string = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # nowTime = time.time()

    # 次に備えて画像を保存
    bef_image = gray_image.copy().astype("float")

    # 動体が無かったら終了
    if max_area < DETECTSIZE:
        return False

    # プッシュ通知を送信
    send_notification()

    # 画像をファイルに保存
    filename = PICK_PATH + "/move_" + now_string + ".jpg"
    cv2.imwrite(filename, img)

    # ログ出力
    print(now_string + ' 動体検知 ' + filename + ' ' + str(max_area))
    return True


def send_notification():
    """
    Android端末へプッシュ通知を送信する
    :return:
    """
    payload = {'notification': "ドアプレート", 'body': "訪問者を検知しました．"}
    headers = {'Authorization': AUTHORIZATION_KEY, 'Content-Type': 'application/json'}
    res = requests.post(URL, headers=headers, data=json.dumps(payload))

    # レスポンスの表示
    print(res.text)

def motion():
    """
    動体検知及び通知を送信を実行する関数
    :return:
    """
    makepicpathdir(PICK_PATH)
    # 撮影，動体検知，県知事のプッシュ通知を行う
    while True:
        photo_path = get_photo(PICK_PATH)
        move = move_detect(cv2.imread(photo_path))
        if move:
            # 動態検知した場合，プッシュ通知を送信
            send_notification()

        # 一時停止
        time.sleep(INTERVAL)


# motion確認用
if __name__ == "__main__":
    makepicpathdir(PICK_PATH)
    try:
        print("Running System, press Ctrl-C to exit")
        # 撮影，動体検知，県知事のプッシュ通知を行う
        while True:
            PHOTO_PATH = get_photo(PICK_PATH)
            MOVE = move_detect(cv2.imread(PHOTO_PATH))
            if MOVE:
                # 動態検知した場合，プッシュ通知を送信
                send_notification()

            # 一時停止
            time.sleep(INTERVAL)

    # Ctrl-Cを押した時
    except KeyboardInterrupt:
        print(KeyboardInterrupt)
