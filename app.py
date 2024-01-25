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
import http.client
from bs4 import BeautifulSoup
import re
import time
from datetime import date
import http.client

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
    rtl = getCurPrice(str(message.text))
    
    if rtl=="":
        rtl="查無資料"
    else:
        rtl = main(str(message.text) + ":" + rtl)        
    message = TextSendMessage(text=rtl)
    line_bot_api.reply_message(event.reply_token, message)

def main(infStock):
    id = infStock.split(":")[0]
    name = infStock.split(":")[1]
    rprice = float(infStock.split(":")[2])
    df1 = pd.DataFrame(getRevenueSurplus(id)) #營收
    df2 = pd.DataFrame(getDividendPolicy(id)) #股利
    today = date.today()
    sYear = today.year-2
    eYear = today.year
    sRt = id + "  " + name + "  " + str(rprice)
    if today.month==1:
        sYear = sYear-1
        eYear = eYear-1
    sRt = ('  年,  月均營收, 股利,    基數,目標價')
    base=0
    Goal=0
    while sYear <= eYear:
        AvMonthlyRevenue = float(getAvMonthlyRevenue(sYear,df1))
        TotalDividend = float(getDividend(sYear,df2))

        if TotalDividend > -1 :
            base = TotalDividend / AvMonthlyRevenue
        else:
            TotalDividend = base*AvMonthlyRevenue
            base=0
    
        Goal=TotalDividend*20
        #base = TotalDividend / AvMonthlyRevenue
        #print(str(sYear) + ',' + str(AvMonthlyRevenue) + ',' +str(round(TotalDividend,2)) + ',' + str(round(base,6)) + ',' + str(round(Goal,2)))
        sRt = sRt + "\n" + (str(sYear) + ',' + str(AvMonthlyRevenue).zfill(10) + ',' +str(round(TotalDividend,2)).zfill(5) + ',' + str(round(base,6)).zfill(8) + ',' + str(round(Goal,2)).zfill(6))
        sYear = sYear + 1
    Percentage=((Goal-rPrice)/rPrice)*100
    Percentage2=((TotalDividend)/rPrice)*100
    sRt = sRt + "\n" + ('預期價差:' + str(round(Goal-rPrice,1)))
    sRt = sRt + "\n" + ('預期獲利:' + str(round(Percentage,1)) + '%')
    sRt = sRt + "\n" + ('預期利息:' + str(round(Percentage2,1)) + '%')
    #print('預期價差:' + str(round(Goal-rPrice,1)))
    #print('預期利息:' + str(round(Percentage2,1)) + '%')
    if Percentage>10:
        sRt = sRt + "\n" + "可否買進:可"
    else:
        sRt = sRt + "\n" + "可否買進:否"
    return sRt

def getAvMonthlyRevenue(tYear,df):
    filt = df['Date'].str.contains(str(tYear), na=False)
    d1 = df.loc[filt, ['MonthlyRevenue']]
    s=pd.to_numeric(pd.Series(d1['MonthlyRevenue']))
    if len(df.loc[filt, ['Date', 'MonthlyRevenue']])==0:
        return 0
    return int(s.sum()/len(df.loc[filt, ['Date', 'MonthlyRevenue']]))/1000
    #print('月均營收:' + str(s.sum()/len(df1.loc[filt, ['Date', 'MonthlyRevenue']])))

def getDividend(tYear,df):
    filt = df['Date'].str.contains(str(tYear), na=False)
    d1 = df.loc[filt, ['TotalDividend']]
    s=pd.to_numeric(pd.Series(d1['TotalDividend']))
    if len(d1)==0:
        return -1
    #print(s1.sum()+s2.sum())
    return str(s.sum())
    #print('月均營收:' + str(s.sum()/len(df1.loc[filt, ['Date', 'MonthlyRevenue']])))

def getRevenueSurplus(tStock):
    ##營收 --- start
    #url = f"https://www.cmoney.tw/finance/f00026.aspx?s={stock_id}"
    url = f"https://www.cmoney.tw/finance/{tStock}/f00029"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)
    soup = BeautifulSoup(res.text,'html.parser')
    # 取得基本資料的cmkey
    for line in soup.find_all(class_="mobi-finance-subnavi-link"):
        if line.text == '營收盈餘':
            cmkey = line['cmkey'].replace('=','%3D').replace('/','%2F').replace('+','%2B')
    
    url = f"https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetStockRevenueSurplus&stockId={tStock}&cmkey={cmkey}"
    # 特別注意要加入Referer
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36',
        'Referer': f"https://www.cmoney.tw/finance/{tStock}/f00029"
    }
    res = requests.get(url,headers=headers)
    return res.json()
    ##營收 --- end

def getDividendPolicy(tstock):
      ## 股利 --- start
      url = f"https://www.cmoney.tw/finance/{tstock}/f00027"
      headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
      res = requests.get(url,headers=headers)
      soup = BeautifulSoup(res.text,'html.parser')
      # 取得基本資料的cmkey
      for line in soup.find_all(class_="mobi-finance-subnavi-link"):
          if line.text == '股利政策':
              cmkey = line['cmkey'].replace('=','%3D').replace('/','%2F').replace('+','%2B')
    
      url = f"https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetDividendPolicy&stockId={tStock}&cmkey={cmkey}"
    
      # 特別注意要加入Referer
      headers = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36',
          'Referer': f"https://www.cmoney.tw/finance/{tStock}/f00027"
      }
    
      res = requests.get(url,headers=headers)
      return res.json()
      ## 股利 --- end

def getCurPrice(tStock):
      headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
      host = "tw.quote.finance.yahoo.net"
      conn = http.client.HTTPSConnection(host)
      qstring = f"/quote/q?type=ta&perd=d&mkt=10&sym={tStock}&v=1&callback=jQuery111302872649618000682_1649814120914&_=1649814120915"
      conn.request("GET", qstring, headers=headers)
      res = conn.getresponse().read().decode()
      sname=res.replace('"','').split('{')[2].split(',')[1].split(':')[1]
    
      if (sname)=="":
          return ""
      # 最新價格
      current = [l for l in res.split('{') if len(l)>=60][-1]
      current = current.replace('"','').split(',')
      price=float(re.search(':.*',current[4]).group()[1:])
      # 昨日價格
      #yday = float(re.search(':.*',[l for l in res.text.split('{') if len(l)>=60][-2].split(',')[4]).group()[1:])
      return sname + ':' + str(price)
    
#import os
if __name__ == "__main__":
    #port = int(os.environ.get('PORT', 8000))
    #app.run(host='0.0.0.0', port=port)
    app.run()
