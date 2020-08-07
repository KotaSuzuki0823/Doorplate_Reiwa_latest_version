'''
GUI
'''
import json
import sys

import PySimpleGUI as sg

import bt

def loadFromAndroid():
    '''
    Bluetoothを用いてAndroidからデータの読み込み
    :return: json
    '''

def onScreen(styledata):
    '''
    GUI表示する部分
    https://qiita.com/dario_okazaki/items/656de21cab5c81cabe59
    :param styledata: Androidから送られてきたJSON形式のデータ
    :return:
    '''
    while(True):
        try:
            json.loads(styledata)
        except json.JSONDecodeError as e:
            print(sys.exc_info())
            print(e)
            continue

        sg.theme(styledata.color)
