####Discordの指定したチャンネルから時刻を読み取り、その時刻になったらspace keyをsendする####
##最初にTerminal内で"Received start time!!と出力されます。そのタイミングでlag timeを入力してください
##スクリプト起動後にチャンネルに再生時刻が打ち込まれると、自動で

# Read the time from a specified Discord channel and send the space key when that time arrives.
# After starting the script, when the playback time is entered in the channel, the message "Received start time!!"
# will be output in the Terminal. At that moment, input the lag time.

##作成者(Author)：高橋紘喜 Takahashi Koki
##日付(Date)：2024/04/24
import discord
from discord.ext import commands
import datetime
from time import ctime
import time
import re
import ntplib
import keyboard
from zoneinfo import ZoneInfo
#BOTのトークン
#第0号
#トークンを打ち込む必要があります．
TOKEN = "aaaaaaaaaaaaaaaaaa"
#チャンネルの指定:入力待ち
#入力を待つチャンネルのIDを打ち込む必要があります．
CHANNEL_ID = 11111111111111111
#チャンネル指定:出力先
#出力先のチャンネルのIDを打ち込む必要があります．
CHANNEL_ID_OUT = 22222222222222222222

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
            if sec<0 or sec>59 or min<0 or min>59 or hour<0 or hour>23:
                 print("error:time is invalid")
                 return -1,-1,-1
            return hour,min,sec
        else:
            print("error:can't recognize input time")
            return -1,-1,-1

##########################################################
ntp_client = ntplib.NTPClient()
#日本標準時 ntp.nict.jp
ntp_server_host = 'ntp.nict.jp'     

intents = discord.Intents.default()
intents.message_content = True
#botオブジェクトの作成。!で始まるものをコマンドとして認識
bot = commands.Bot(command_prefix='!', intents=intents)
#Clientオブジェクト作成
#client = discord.Client(intents=intents)
#出力先のチャンネルを指定する領域
global output_channel
output_channel = None

#inputを最初に
####ラグの入力####
####input lag_time####
lag_time=float(input("Input lag time -2 or more, like \"0.250\" or \"-1.30\":"))


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    global output_channel
    output_channel = bot.get_channel(CHANNEL_ID_OUT)
    if output_channel is None:
        print(f"Could not find channel with ID: {CHANNEL_ID_OUT}")
    else:
        print(f"Output channel set to: {output_channel.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    else:
        #指定したチャンネルのみに反応
        if message.channel.id == CHANNEL_ID:
            print(f"Message content: '{message.content}'")
            print(f"Channel ID: {message.channel.id}")
            #こんにちはと言われたらこんにちはと返す
            if message.content == 'こんにちは':
                if output_channel is not None:
                    await output_channel.send('こんにちは！') 
                    print(f"Message from {message.author}: {message.content}")
                else:
                    print("Output channel is not set.")
                return 
            #messageから時刻を抽出
            #初期値
            hour,minu,sec = -1,-1,-1
            #日付抽出
            hour,minu,sec = readtime(message.content)
            #日付抽出可能の場合
            if hour !=-1 and minu !=-1 and sec != -1:
                waiting = 0.0
                print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                print("Received start time!!")
                await output_channel.send("Received start time!!")
                #今日の日付(jst)
                now_jst = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
                #target_timeの作成(jst)
                target_time = datetime.datetime(now_jst.year,now_jst.month,now_jst.day,hour,minu,sec,tzinfo = ZoneInfo(key='Asia/Tokyo'))
                #target_timeをUTCに変換
                utc_target_time = target_time.astimezone(datetime.timezone.utc)
                #utc_target_timeを計算可能なタイムスタンプ型に
                ts = datetime.datetime.timestamp(utc_target_time)

                print("NOW_UTC:",ts)
                

                #ntpserverへの問い合わせ
                res = ntp_client.request(ntp_server_host)
                waiting = ts - res.tx_time
                
                print("NTP:",res.tx_time)

                #nowtime = datetime.datetime.strptime(ctime(res.tx_time), "%a %b %d %H:%M:%S %Y")
                #print("NOW:",nowtime.strftime('%Y/%m/%d %H:%M:%S')) 

                if waiting<0:
                    print("error: you imput past time")
                    print("input time one more time")
                    await output_channel.send('error: you imput past time')
                    await output_channel.send('input time one more time')
            
            #日付抽出不可能な場合
            else:
                print("invalid time was input")
                await output_channel.send('invalid time was input')
                return
            
            print("wait", waiting + lag_time, "s")

            #待ち時間が負の場合
            if waiting<0:
                print("error: you imput past time")
                print("please try again")
                await output_channel.send('error: you imput past time')
                await output_channel.send('please try again')

            #待ち時間設定に異常なしの場合
            else:
                time.sleep(waiting+lag_time)
            keyboard.send("space")
            print("done")
            await output_channel.send("done")
            print("thank you for using!")
            print("press Ctrl + C to quit")

            ##データの初期化##
            #初期値
            hour,minu,sec = -1,-1,-1
            
            print("\n\n")
            return

bot.run(TOKEN)
