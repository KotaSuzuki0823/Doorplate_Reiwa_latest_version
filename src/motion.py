"""
ラズパイカメラで動体検知し，Android端末に通知
参考：https://dream-soft.mydns.jp/blog/developper/smarthome/2020/02/678/#toc6
"""

import time
import datetime
import subprocess
import os
import sys
import cv2

# プッシュ通知用
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

# ホームディレクトリのパス
HOME = os.environ['HOME']
# 画像の格納パス
# PICK_PATH = HOME + '/camera/picts'

# Push通知のURL
URL = 'https://fcm.googleapis.com/fcm/send'

# サーバ通知のインターバル(秒)
INTERVAL = 30

# 動体検知の精度
DETECTSIZE = 1000

# プッシュ通知の認証キー
# This registration token comes from the client FCM SDKs.
AUTHORIZATION_KEY = 'cHJ73QDYQA-Jj0vnMrxvqg:APA91bEKOF5aF-S-g9iXifJ77ggq6A46j57OY8XEaY9AKCN-4IDMRJ4MIi8geUSpRYzu91P95R7uC_NmuuL4SmdzrW1YuqZe5daMd9i4VQnl0ZG-gEd_j7dsY5KCVhxB8UtAHU1ikC-8'

CRED = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(CRED)

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

class MotionDetect:
    """
    動体検知
    """
    def __init__(self, picpath=HOME + '/camera/picts'):
        self.__authorization_key: str = ""
        self.pick_path = picpath
        self.bef_image = None
        self.makepicpathdir()

    def makepicpathdir(self):
        """
        撮影した写真を格納するディレクトリを作成する関数
        :param path: 保存先のパス
        :return:
        """
        try:
            os.makedirs(self.pick_path)
            print('Created the Directory(' + self.pick_path + ') ')
        except FileExistsError:
            return

    # @staticmethod
    def move_detect(self, img):
        """
        最新の写真と1つ前の写真を比較して，差分から動体検知をする
        :parm:img cv2のImage型変数 最新の写真
        :return:　bool型　検知結果
        """
        #global bef_image

        # 入力画像をグレースケールに変換
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 前画像がない場合、現画像を保存し終了
        if self.bef_image is None:
            self.bef_image = gray_image.copy().astype("float")
            print('Before image is not found. (bef_image is None) ')
            return False

        # 前画像との差分を取得する
        cv2.accumulateWeighted(gray_image, self.bef_image, 0.00001)
        delta = cv2.absdiff(gray_image, cv2.convertScaleAbs(self.bef_image))
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
        self.bef_image = gray_image.copy().astype("float")

        # 動体が無かったら終了
        if max_area < DETECTSIZE:
            return False

        # 画像をファイルに保存
        filename = self.pick_path + "/move_" + now_string + ".jpg"
        cv2.imwrite(filename, img)

        # ログ出力
        print(now_string + ' 動体検知 ' + filename + ' ' + str(max_area))
        return True


    def send_notification(self):
        """
        Android端末へプッシュ通知を送信する
        :return:
        """

        # See documentation on defining a message payload.
        message = messaging.Message(
            notification=messaging.Notification(
                title='ドアプレート',
                body='訪問者を検知しました',
            ),
            token=self.__get_token(),
        )

        # Send a message to the device corresponding to the provided
        # registration token.
        response = messaging.send(message)
        # Response is a message ID string.
        print('Successfully sent message:', response)

    def update_token(self, token: str):
        """
        Firebaseトークンキーの更新
        """
        __authorization_key = token
        print("Update token key")

    def __get_token(self):
        return self.__authorization_key

    def motion(self):
        """
        動体検知及び通知を送信を実行する関数
        :return:
        """
        # makepicpathdir(self.pick_path)
        # 撮影，動体検知，県知事のプッシュ通知を行う
        while True:
            photo_path = get_photo(self.pick_path)
            move = self.move_detect(cv2.imread(photo_path))
            if move:
                # 動態検知した場合，プッシュ通知を送信
                self.send_notification()

            # 一時停止
            time.sleep(INTERVAL)

if __name__ == "__main__":
    test = MotionDetect()
    test.update_token("fj-wiPY4QIauOupmBf6gfV:APA91bH04B6B6huYRRi4tKAe6N3fCJd-6rFV64X6DPkmBE7CwMm__alEVb3b_aT3pk_11gtlAL89JOMI95mAa7Lj5Na5REovGD7VheG5xDie2eK_tTVEBorMBXWHy8kJ4u4SKHIKNu1J")
    test.motion()
