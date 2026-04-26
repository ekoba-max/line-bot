from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

import os

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 簡易DB（本来はDB使う）
user_data = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400

    return 'OK'

from linebot.models import MessageEvent, TextMessage

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    if user_id not in user_data:
        user_data[user_id] = {"step": 0}

    step = user_data[user_id]["step"]

    if step == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="年齢を教えてください")
        )
        user_data[user_id]["step"] = 1

    elif step == 1:
        user_data[user_id]["age"] = text
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="職業を教えてください")
        )
        user_data[user_id]["step"] = 2

    elif step == 2:
        user_data[user_id]["job"] = text
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="今の悩みを教えてください")
        )
        user_data[user_id]["step"] = 3

    elif step == 3:
        user_data[user_id]["problem"] = text

        # 興味度判定（簡易）
        if "稼ぎたい" in text or "副業" in text:
            msg = "こちらから面談予約できます\nhttps://calendly.com/あなたのURL"
        else:
            msg = "まずはこちらをご覧ください"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )

        user_data[user_id]["step"] = 0

if __name__ == "__main__":
    app.run()
