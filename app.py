#from flask import Flask, request, abort
#from linebot import LineBotApi, WebhookHandler
#from linebot.exceptions import InvalidSignatureError
#from linebot.models import *
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import date

app = Flask(__name__)

#line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
#handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
YOUR_CHANNEL_ACCESS_TOKEN = 'Sr7FHElXR68M+nJNdDMqp6w4zh8wDKubzOndLyaabKdaqC9mY1My4J3GzyLPnIjUxGm36zxZjCFQrbTLjx98MoAn7RakgFbb6JTOA/jHdVb3D9R5sSv95UrpN5z4Be/J3H+chlMS/R30zgZ/yF5RjQdB04t89/1O/w1cDnyilFU='
YOUR_CHANNEL_SECRET = '1437f2ed3f6cbbcbe6033976c1a34d64'

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    message = getCurPrice(message)
    if message=="":
        message="查無資料"
    line_bot_api.reply_message(event.reply_token, message)

def getCurPrice(tStock):
    url = f"https://tw.quote.finance.yahoo.net/quote/q?type=ta&perd=d&mkt=10&sym={tStock}&v=1&callback=jQuery111302872649618000682_1649814120914&_=1649814120915"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)

    sname=res.text.replace('"','').split('{')[2].split(',')[1].split(':')[1]

    return str(sname)
    if (sname)=="":
      return ""
    # 最新價格
    current = [l for l in res.text.split('{') if len(l)>=60][-1]
    current = current.replace('"','').split(',')
    #print(res.text.split('{')[2])
    price=float(re.search(':.*',current[4]).group()[1:])
    # 昨日價格
    #yday = float(re.search(':.*',[l for l in res.text.split('{') if len(l)>=60][-2].split(',')[4]).group()[1:])
    return sname + ':' + price
    
#import os
if __name__ == "__main__":
    #port = int(os.environ.get('PORT', 8000))
    #app.run(host='0.0.0.0', port=port)
    app.run()
