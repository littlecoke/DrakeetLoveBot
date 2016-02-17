# coding: utf-8

from datetime import datetime

from flask import Flask
from flask import render_template, request
import logging
import telegram

# from views.todos import todos_view

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 动态路由
# app.register_blueprint(todos_view, url_prefix='/todos')
global bot
# 由于 美国节点，只能 git 部署，我不得不开源 token，请不要随便拿去用，如需生成你自己的 token
# 请联系 http://telegram.me/BotFather 谢谢！
bot = telegram.Bot(token='192666820:AAHLcmxXJ68UvkB-nWgbPVGzb_bkDoTNlcU')

@app.route('/')
def index():
    return r'{"drakeet":"hehe"}'


@app.route('/<token>', methods=['POST'])
def echo(token):
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True))
        chat_id = update.message.chat.id
        # Telegram understands UTF-8, so encode text for unicode compatibility
        text = update.message.text.encode('utf-8')
        if '/echo ' in text:
            text = text[6:]
        # repeat the same message back (echo)
        bot.sendMessage(chat_id=chat_id, text=text)
    return 'ok'
