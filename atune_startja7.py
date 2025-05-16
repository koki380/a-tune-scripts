#a-tune 動画再生

#NTP サーバから時刻をとる
#(再生開始時刻に与えたい遅延時間を足した時刻) - NTP サーバからとった時刻 を計算
#その時刻だけ wait()
#クリック


#NTPサーバーは一旦固定値
#https://qiita.com/komorin0521/items/63203f0c3fcea0f40a87
#日本のntpサーバー一覧。
#http://codenight.com/ntp/
#google ntp server
#https://developers.google.com/time/

import datetime
from time import ctime
import time

# please install module using pip-
# (sudo) pip installntp lib
import ntplib
import keyboard
#from pynput.keyboard import Key, Controller
import re

#時刻入力パターン
time_type = re.compile(r"""(
    #以下、時刻
    (\d{1,2})       # 1 or 2 digits number
    (\D{0,1})
    (\d{1,2})       # 1 or 2 digits number
    (\D{0,1})
    (\d{1,2})       # 1 or 2 digits number
    )""",re.VERBOSE | re.IGNORECASE)

def readtime(input):
        #コンパイルした正規表現パターンで日付と時刻を抽出
        input_day = time_type.search(input)
        bool_value = bool(input_day)
        if bool_value is True:
            split = input_day.groups()       #要素ごとにsplitへ
            # for i in range(len(split)):
            #     print(split[i])
            sec = int(split[5])
            min = int(split[3])
            hour = int(split[1])
            
            #以下、エラーチェック
            if sec<0 or sec>59 or min<0 or min>59 or hour<1 or hour>23:
                 print("error:time is invalid")
                 return -1,-1,-1
            return hour,min,sec
        else:
            print("error:can't recognize input time")
            return -1,-1,-1


ntp_client = ntplib.NTPClient()
#日本標準時 ntp.nict.jp
ntp_server_host = 'ntp.nict.jp'     

#初期値
hour,minu,sec = -1,-1,-1
#入力成功フラグ
input_flag = False
while(1):
    while(1):
        #何時にクリックするのかを指定する
        input_time=str(input("Input start time like \"13:30:20\",or Enter Ctrl + C to quit:"))
        #日付抽出
        hour,minu,sec = readtime(input_time)
        #日付抽出可能の場合
        if hour !=-1 and minu !=-1 and sec != -1:
            #今日の日付
            dt_today = datetime.datetime.today()
            #target_timeの作成
            target_time = datetime.datetime(dt_today.year,dt_today.month,dt_today.day,hour,minu,sec)
            #入力値を計算可能なタイムスタンプ型に
            ts = datetime.datetime.timestamp(target_time)

            #ntpserverへの問い合わせ
            res = ntp_client.request(ntp_server_host)
            waiting = ts - res.tx_time

            nowtime = datetime.datetime.strptime(ctime(res.tx_time), "%a %b %d %H:%M:%S %Y")
            print("NOW:",nowtime.strftime('%Y/%m/%d %H:%M:%S'))

            if waiting<0:
                print("error: you imput past time")
                print("input time one more time")
            else:
                break
        else:
            print("input time one more time")
        

    #さらにそこからラグを指定。-2以上の値のみ入力可能
    lag_time=float(input("Input lag time -2 or more, like \"0.250\" or \"-1.30\":"))
    #target_time = "2022-10-24 12:44:00"

    #ntpサーバーに問い合わせ。
    res = ntp_client.request(ntp_server_host)
    nowtime = datetime.datetime.strptime(ctime(res.tx_time), "%a %b %d %H:%M:%S %Y")


    #ntpサーバーに問い合わせた結果を出力
    #print("now time:",nowtime.strftime('%Y/%m/%d %H:%M:%S'))

    #現時刻を計算するための形に変更して出力
    #print(res.tx_time)

    waiting = ts - res.tx_time
    #print(ts)
    print("wait", waiting + lag_time, "s")




    if waiting<0:
        print("error: you imput past time")
        print("please try again")

    else:   
        #指定時刻3秒前まで待つ
        time.sleep(waiting-3.000)

        print(3+lag_time, "second left...")

        
        #再びntpサーバーに問い合わせ。
        #この際、問い合わせにかかった時間を記録し後でsleepする。    
        ntp_start_time=time.perf_counter()
        res = ntp_client.request(ntp_server_host)
        ntp_end_time=time.perf_counter()


        waiting2=ts-res.tx_time
        waiting3=(ntp_end_time-ntp_start_time)/2
        #print("waiting3=",waiting3)

        time.sleep(waiting2+waiting3+lag_time)

        keyboard.send("space")
        print("done")
        print("thank you for using!")
        print("press Ctrl + C to quit")
        
        ##データの初期化##
        #初期値
        hour,minu,sec = -1,-1,-1
        #入力成功フラグ
        input_flag = False
        print("\n\n")

