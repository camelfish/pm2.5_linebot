from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, LocationMessage, TemplateSendMessage, PostbackEvent,
    ButtonsTemplate, CarouselTemplate, PostbackTemplateAction, CarouselColumn, URITemplateAction, MessageTemplateAction, SourceUser
)

import requests
import googlemaps
import numpy as np
import json
import os
from chatbase import Message

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('+6Vcg6zNfbqzQTPZF3hx8svapB2CFA1QyTrObKNMMdcOS0WUsB7KNataArmQLHj4K/H9y99ayvbt5HGCLf85zkjcuCfAL35H8H1HhdkhhBszkwBYuIGClUZkqopuPKydtv2tGMDQ7bFlcFaAU4NbZQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('509073f22655c9158ec62aa059de1a32')
#GoogleMap key

static_maps_api_key = 'AIzaSyAVm5OZ1LB1WkPuGzfaO51my37yW2qGkJY'
gmaps = googlemaps.Client(key='AIzaSyB25oVe3hd7XD-0kG0vWyRKfmIyDAX1YsU')
#google_map_api = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' +loc+ '&key=AIzaSyB25oVe3hd7XD-0kG0vWyRKfmIyDAX1YsU').json()
chatbase_api_key = '8724d1e0-8ab2-4b41-998f-2eeabd8cb189'

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
    
    profile = line_bot_api.get_profile(event.source.user_id)

    loc_dis_min={}
    nearest_loc = []

    user_loc = event.message.text
    gecode_result = gmaps.geocode(user_loc)
    user_loc_abs = np.array(list(gecode_result[0]['geometry']['location'].values()))

    for i in data_pm['feeds']:

        device_loc_abs = np.array([i['gps_lat'],i['gps_lon']])

        #Euclidean Distance between two location
        loc_dis=np.sqrt(np.sum(np.square(user_loc_abs-device_loc_abs)))
        loc_dis_min[i['device_id']] = [i['s_d0'], loc_dis, i['gps_lat'], i['gps_lon']]

    loc_dis_min = sorted(loc_dis_min.items(), key=lambda e: e[1][1])

    
    for i in range(5):
        gecode_result = gmaps.reverse_geocode((loc_dis_min[i][1][2], loc_dis_min[i][1][3]), language='zh-TW')
        nearest_loc.append(gecode_result[0]['formatted_address'])

    for i in nearest_loc:
        print(i)

    print(loc_dis_min[0][1][0])

    #滾軸
    carousel_template = CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[0][1][2])+','+ str(loc_dis_min[0][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[0][1][2])+','+ str(loc_dis_min[0][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[0][3:23],
                text = 'pm2.5為'+str(loc_dis_min[0][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label='貼心小提醒', 
                        data=str(loc_dis_min[0][1][0]),
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[1][1][2])+','+ str(loc_dis_min[1][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[1][1][2])+','+ str(loc_dis_min[1][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[1][3:23],
                text = 'pm2.5為'+str(loc_dis_min[1][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label = '貼心小提醒', 
                        data=str(loc_dis_min[1][1][0]),
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[2][1][2])+','+ str(loc_dis_min[2][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[2][1][2])+','+ str(loc_dis_min[2][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[2][3:23],
                text = 'pm2.5為'+str(loc_dis_min[2][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label = '貼心小提醒', 
                        data=str(loc_dis_min[2][1][0]),
                    )
                ]
            ),                    
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[3][1][2])+','+ str(loc_dis_min[3][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[3][1][2])+','+ str(loc_dis_min[3][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[3][3:23],
                text = 'pm2.5為'+str(loc_dis_min[3][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label = '貼心小提醒', 
                        data=str(loc_dis_min[3][1][0]),
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[4][1][2])+','+ str(loc_dis_min[4][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[4][1][2])+','+ str(loc_dis_min[3][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[4][3:23],
                text = 'pm2.5為'+str(loc_dis_min[4][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label = '貼心小提醒', 
                        data=str(loc_dis_min[4][1][0]),
                    )
                ]
            )
        ]
        
    )

    template_message = TemplateSendMessage(
        alt_text = '距離最近的五個測站', 
        template = carousel_template
    )
    print (profile.display_name )

    line_bot_api.reply_message(event.reply_token, template_message)

    msg = Message(api_key=chatbase_api_key,
          type="user",
          platform="Line",
          version="1.0",
          user_id=profile.display_name,
          message=event.message.text,
          intent="LinebotSearchPostion",  
          not_handled=False,           
          )            
    resp = msg.send()

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):

    profile = line_bot_api.get_profile(event.source.user_id)

    # Geocoding an address
    loc_dis_min={}
    nearest_loc = []

    print(event.message.latitude)
    print(event.message.longitude)

    user_loc_abs = np.array([event.message.latitude, event.message.longitude])

    for i in data_pm['feeds']:

        device_loc_abs = np.array([i['gps_lat'],i['gps_lon']])

        #Euclidean Distance between two location
        loc_dis=np.sqrt(np.sum(np.square(user_loc_abs-device_loc_abs)))
        loc_dis_min[i['device_id']] = [i['s_d0'], loc_dis, i['gps_lat'], i['gps_lon']]

    loc_dis_min = sorted(loc_dis_min.items(), key=lambda e: e[1][1])

    
    for i in range(5):
        gecode_result = gmaps.reverse_geocode((loc_dis_min[i][1][2], loc_dis_min[i][1][3]), language='zh-TW')
        nearest_loc.append(gecode_result[0]['formatted_address'])

    #滾軸
    carousel_template = CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[0][1][2])+','+ str(loc_dis_min[0][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[0][1][2])+','+ str(loc_dis_min[0][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[0][3:23],
                text = 'pm2.5為'+str(loc_dis_min[0][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label='貼心小提醒', 
                        data=str(loc_dis_min[0][1][0]),
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[1][1][2])+','+ str(loc_dis_min[1][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[1][1][2])+','+ str(loc_dis_min[1][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[1][3:23],
                text = 'pm2.5為'+str(loc_dis_min[1][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label = '貼心小提醒', 
                        data=str(loc_dis_min[1][1][0]),
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[2][1][2])+','+ str(loc_dis_min[2][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[2][1][2])+','+ str(loc_dis_min[2][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[2][3:23],
                text = 'pm2.5為'+str(loc_dis_min[2][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label = '貼心小提醒', 
                        data=str(loc_dis_min[2][1][0]),
                    )
                ]
            ),                    
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[3][1][2])+','+ str(loc_dis_min[3][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[3][1][2])+','+ str(loc_dis_min[3][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[3][3:23],
                text = 'pm2.5為'+str(loc_dis_min[3][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label = '貼心小提醒', 
                        data=str(loc_dis_min[3][1][0]),
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?center='+ str(loc_dis_min[4][1][2])+','+ str(loc_dis_min[4][1][3])+'&zoom=16&markers=color:blue%7Clabel:S%7C'+ str(loc_dis_min[4][1][2])+','+ str(loc_dis_min[3][1][3])+'&size=600x300&key='+static_maps_api_key,
                title = nearest_loc[4][3:23],
                text = 'pm2.5為'+str(loc_dis_min[4][1][0]),
                actions=[
                    PostbackTemplateAction(
                        label = '貼心小提醒', 
                        data=str(loc_dis_min[4][1][0]),
                    )
                ]
            )
        ]
        
    )

    template_message = TemplateSendMessage(
        alt_text = '距離最近的五個測站', 
        template = carousel_template
    )
    
    line_bot_api.reply_message(event.reply_token, template_message)

    msg = Message(api_key=chatbase_api_key,
              type="user",
              platform="Line",
              version="1.0",
              user_id=profile.display_name,
              message=event.message.address,
              intent="LinebotSearchPostion",  
              not_handled=False,           
              )            
    resp = msg.send()

@handler.add(PostbackEvent)
def handle_postback(event):
    
    #判別空汙等級        
    if float(event.postback.data) <= 11:
        pm_level = '第一等級'
        pm_advice = '(一般民眾)正常戶外活動。\n(敏感性族群)正常戶外活動。'
    elif 12 <= float(event.postback.data) <= 23:
        pm_level = '第二等級'
        pm_advice = '(一般民眾)正常戶外活動。\n(敏感性族群)正常戶外活動。'
    elif 24 <= float(event.postback.data) <= 35:
        pm_level = '第三等級'
        pm_advice = '(一般民眾)正常戶外活動。\n(敏感性族群)正常戶外活動。'
    elif 36 <= float(event.postback.data) <= 41:
        pm_level = '第四等級'
        pm_advice = '(一般民眾)正常戶外活動。\n(敏感性族群)有心臟、呼吸道及心血管疾病的成人與孩童感受到癥狀時，應考慮減少體力消耗，特別是減少戶外活動。'
    elif 42 <= float(event.postback.data) <= 47:
        pm_level = '第五等級'
        pm_advice = '(一般民眾)正常戶外活動。\n(敏感性族群)有心臟、呼吸道及心血管疾病的成人與孩童感受到癥狀時，應考慮減少體力消耗，特別是減少戶外活動。'
    elif 48 <= float(event.postback.data) <= 53:
        pm_level = '第六等級'
        pm_advice = '(一般民眾)正常戶外活動。\n(敏感性族群)有心臟、呼吸道及心血管疾病的成人與孩童感受到癥狀時，應考慮減少體力消耗，特別是減少戶外活動。'
    elif 54 <= float(event.postback.data) <= 58:
        pm_level = '第七等級'
        pm_advice = '(一般民眾)任何人如果有不適，如眼痛，咳嗽或喉嚨痛等，應該考慮減少戶外活動。\n(敏感性族群)1.有心臟、呼吸道及心血管疾病的成人與孩童，應減少體力消耗，特別是減少戶外活動。\n2.老年人應減少體力消耗。\n3.具有氣喘的人可能需增加使用吸入劑的頻率。'
    elif 59 <= float(event.postback.data) <= 64:
        pm_level = '第八等級'
        pm_advice = '(一般民眾)任何人如果有不適，如眼痛，咳嗽或喉嚨痛等，應該考慮減少戶外活動。\n(敏感性族群)1.有心臟、呼吸道及心血管疾病的成人與孩童，應減少體力消耗，特別是減少戶外活動。\n2.老年人應減少體力消耗。\n3.具有氣喘的人可能需增加使用吸入劑的頻率。'
    elif 65 <= float(event.postback.data) <= 70:
        pm_level = '第九等級'
        pm_advice = '(一般民眾)任何人如果有不適，如眼痛，咳嗽或喉嚨痛等，應該考慮減少戶外活動。\n(敏感性族群)1.有心臟、呼吸道及心血管疾病的成人與孩童，應減少體力消耗，特別是減少戶外活動。\n2.老年人應減少體力消耗。\n3.具有氣喘的人可能需增加使用吸入劑的頻率。'
    elif float(event.postback.data) >= 71:
        pm_level = '第十等級'
        pm_advice = '(一般民眾)任何人如果有不適，如眼痛，咳嗽或喉嚨痛等，應減少體力消耗，特別是減少戶外活動。\n(敏感性族群)1.有心臟、呼吸道及心血管疾病的成人與孩童，應減少體力消耗，特別是減少戶外活動。\n2.具有氣喘的人可能需增加使用吸入劑的頻率。'

    reply_mes = '◆等級:' +pm_level+ '\n◆貼心小建議:' +pm_advice

    output_mes = TextSendMessage(text=reply_mes)

    line_bot_api.reply_message(
        event.reply_token,
        output_mes)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

