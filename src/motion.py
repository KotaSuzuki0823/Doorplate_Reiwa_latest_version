'''
ラズパイカメラで動体検知し，Android端末に通知
参考：https://dream-soft.mydns.jp/blog/developper/smarthome/2020/02/678/#toc6
'''

import time
import datetime
import requests
import subprocess
import json
import cv2

# 画像の格納パス
pictpath = '/home/pi/camera/picts'

# Push通知のURL
url = 'https://fcm.googleapis.com/fcm/send'

# サーバ通知のインターバル(秒)
interval = 30

# 動体検知の精度
detectSize = 1000

# プッシュ通知の認証キー
AUTHORIZATION_KEY = 'key=AAAAlNSzCwE:APA91bHCIcrJeRbN13m2QEY5pXjgzwpQ_q5L6qlcdBk1NJQFx2ffGxja9EHrg62Zd_sNm_r6C6HIuRKkNjygo0WhuHuYc7mGSwFGBGXiR44G6S80gKMtr3TtwnFbh4eIepOMRT8nHn7c'

def getPhoto(photopath):
    """
    ラズパイカメラで写真を撮影
    :return:
    """
    cmd = ["raspistill", "-t", "2000", "-o", photopath]
    print("Run raspistill...")
    try:
        subprocess.check_call(cmd)
        takePhotoTime = datetime.datetime.now()
    except Exception as e:
        print("subprocess.check_call() failed:"+ e)
        return

@staticmethod
def moveDetect(img):
    """
    最新の写真と1つ前の写真を比較して，差分から動体検知をする
    :parm:img cv2のImage型変数 最新の写真
    :return:
    """
    global befImg

    # 入力画像をグレースケールに変換
    grayImg=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 前画像がない場合、現画像を保存し終了
    if befImg is None:
        befImg = grayImg.copy().astype("float")
        return

    # 前画像との差分を取得する
    cv2.accumulateWeighted(grayImg, befImg, 0.00001)
    delta = cv2.absdiff(grayImg, cv2.convertScaleAbs(befImg))
    thresh = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]
    image, contours, h = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  

    # 画像内の最も大きな差分を求める
    max_area=0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if max_area < area:
            max_area = area
    
    # 現在時間を取得
    nowStr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nowTime = time.time()

    # 次に備えて画像を保存
    befImg = grayImg.copy().astype("float")

    # 動体が無かったら終了
    if max_area < detectSize:
        return
    
    # プッシュ通知を送信
    sendNotificationToAndroid()

    # 画像をファイルに保存
    filename = pictpath+"/move_"+nowStr+".jpg"
    cv2.imwrite(filename, img)

    # ログ出力
    print(nowStr+' 動体検知 '+filename+' '+str(max_area))

def sendNotificationToAndroid():
    """
    Android端末へプッシュ通知を送信する
    :return:
    """
    payload = {'notification': "ドアプレート", 'body': "訪問者を検知しました．"}
    headers = {'Authorization': AUTHORIZATION_KEY, 'Content-Type': 'application/json'}
    r = requests.post(url,params=payload, data=json.dumps(payload))

    print(r.text)

if __name__ == "__main__":
    pass
