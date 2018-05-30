from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)
import requests
import googlemaps
import numpy as np
import json
import os

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('+6Vcg6zNfbqzQTPZF3hx8svapB2CFA1QyTrObKNMMdcOS0WUsB7KNataArmQLHj4K/H9y99ayvbt5HGCLf85zkjcuCfAL35H8H1HhdkhhBszkwBYuIGClUZkqopuPKydtv2tGMDQ7bFlcFaAU4NbZQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('509073f22655c9158ec62aa059de1a32')
#GoogleMap key
gmaps = googlemaps.Client(key='AIzaSyB25oVe3hd7XD-0kG0vWyRKfmIyDAX1YsU')
#google_map_api = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' +loc+ '&key=AIzaSyB25oVe3hd7XD-0kG0vWyRKfmIyDAX1YsU').json()

data_pm = requests.get("https://pm25.lass-net.org/data/last-all-airbox.json").json()

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    print('receive message')
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    loc_dis_min = 1000
    device_id_min = ''
    pm25_min = 0

    user_loc = event.message.text
    gecode_result = gmaps.geocode(user_loc)
    #the [lat, lon] of user_loc
    user_loc_abs = np.array(list(gecode_result[0]['geometry']['location'].values()))

    for i in data_pm['feeds']:
        device_loc_abs = np.array([i['gps_lat'],i['gps_lon']])

        #Euclidean Distance between two location
        loc_dis=np.sqrt(np.sum(np.square(user_loc_abs-device_loc_abs)))

        if loc_dis_min == 1000:
            loc_dis_min = loc_dis
            device_id_min = i['device_id']
            pm25_min = i['s_d0']
        
        elif loc_dis < loc_dis_min:
            loc_dis_min = loc_dis
            device_id_min = i['device_id']
            pm25_min = i['s_d0']

    #判別空汙等級        
    if pm25_min <= 50:
        pm_level = '良好'
    elif pm25_min >= 51 & pm25_min <= 100:
        pm_level = '普通'
    elif pm25_min >= 101 & pm25_min <= 150:
        pm_level = '對敏感族群不健康'
    elif pm25_min >= 151 & pm25_min <= 200:
        pm_level = '對所有族群不健康'
    elif pm25_min >= 201 & pm25_min <= 300:
        pm_level = '非常不健康'
    elif pm25_min >= 301 & pm25_min <= 500:
        pm_level = '危害'

    reply_mes = '距離' +user_loc+ '最近的pm2.5是' +str(pm25_min)+ '。\npm2.5的等級屬於' +pm_level

    output_mes = TextSendMessage(text=reply_mes)

    line_bot_api.reply_message(
        event.reply_token,
        output_mes)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

