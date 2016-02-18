# coding: utf-8

from datetime import datetime

from flask import Flask
from flask import render_template, request
import logging
import telegram


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
bot_name = '@DrakeetLoveBot'

global bot
# 由于 美国节点，只能 git 部署，我不得不开源 token，请不要随便拿去用，如需生成你自己的 token
# 请联系 http://telegram.me/BotFather 谢谢！
bot = telegram.Bot(token='192666820:AAHLcmxXJ68UvkB-nWgbPVGzb_bkDoTNlcU')

@app.route('/')
def index():
    return r'{"drakeet":"hehe"}'


@app.route('/<token>', methods=['POST'])
def launcher(token):
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True))
        logging.info('I am still alive.')
        handle_message(update.message)
    return 'ok'


def handle_message(message):
    text = message.text
    if '/echo' in text:
        echo(message)
    if '/milestone' in text:
        milestone(message)


def parse_cmd_text(text):
    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = text.encode('utf-8')
    cmd = None
    if '/' in text:
        try:
            index = text.index(' ')
        except ValueError as e:
            return (text, None)
        cmd = text[:index]
        text = text[index + 1:]
    if not cmd == None and '@' in cmd:
        cmd = cmd.replace(bot_name, '')
    return (cmd, text)


def echo(message):
    '''
    repeat the same message back (echo)
    '''
    cmd, text = parse_cmd_text(message.text)
    if text == None or len(text) == 0:
        pass
    else:
        chat_id = message.chat.id
        bot.sendMessage(chat_id=chat_id, text=text)


def milestone(message):
    from_day = datetime(2013, 7, 16)
    now = datetime.now()
    text = 'drakeet 和他家老婆大人已经认识并相爱 %d 天啦' % (now - from_day).days
    chat_id = message.chat.id
    bot.sendMessage(chat_id=chat_id, text=text)
