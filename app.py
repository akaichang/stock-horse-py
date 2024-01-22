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
    line_bot_api.reply_message(event.reply_token, message)

#import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    #app.run()
