# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Flask
from flask import render_template, request
import logging
import telegram
import leancloud
from leancloud import Engine, Query, Object, LeanCloudError
import random
import re
import sys
import urllib2
import json

reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
bot_name = '@XiaoaiBot'

global bot
# 由于 美国节点，只能 git 部署，我不得不开源 token，请不要随便拿去用，如需生成你自己的 token
# 请联系 http://telegram.me/BotFather 谢谢！
bot = telegram.Bot(token='194363679:AAEUbDAhPiq-Y_6dmwhkHmWvaBj1pTfRDKc')
songci_api = 'http://api.jisuapi.com/songci/search?appkey=7528478e273bd00b&keyword='

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
    elif '/milestone' in text:
        milestone(message)
    elif '/help' in text:
        help(message)
    elif '/getmylastat' in text:
        get_my_last_at(message)
    elif '/pic' in text:
        pic(message)
    elif '/delpic' in text:
        delpic(message)
    elif '/songci' in text:
        songci(message)

    if not '/' in text and '@' in text:
        save_at_message(message)
    logging.info(text)


def help(message):
    text = ('/echo - Repeat the same message back\n'
            '/milestone - Get drakeet\'s milestone\n'
            '/getmylastat - Get my last @ message\n'
            '/pic - Curiosity killed the cat\n'
            '/delpic - Delete pic by its num\n'
            '/songci - TEXT')
    bot.sendMessage(chat_id=message.chat.id, text=text)



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
    text = 'drakeet 和他家老婆大人已经认识并相爱 %d 天啦（此处应该有恭喜' % (now - from_day).days
    chat_id = message.chat.id
    bot.sendMessage(chat_id=chat_id, text=text)


def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile):
      if random.randrange(num + 2): continue
      line = aline
    return line


def random_text(message):
    '''
    Deprecated
    '''
    Text = Object.extend('Text')
    _query = Query(Text)
    count = _query.count()
    skip = random.randint(0, count - 1)
    texts = _query.limit(1).skip(skip).find()
    if len(texts) == 1:
        text = texts[0]
    else:
        return
    bot.sendMessage(chat_id=message.chat.id, text=text)


AtMessage = Object.extend('AtMessage')


def save_at_message(message):
    msg = AtMessage()
    try:
        username = re.findall(r'@(\w*)\s', message.text)[0]
    except IndexError as e:
        return
    msg.set('owner', username)
    msg.set('mid', message.message_id)
    msg.set('chat_id', message.chat.id)
    msg.save()


def get_my_last_at(message):
    '''
    todo: relate the origin chat id.
    '''
    query = Query(AtMessage)
    query.descending('createdAt')
    query.equal_to('owner', message.from_user.username)
    query.equal_to('chat_id', message.chat.id)
    try:
        msg = query.first()
    except LeanCloudError as e:
        bot.sendMessage(chat_id=message.chat.id, reply_to_message_id=message.message_id, text='你在本群还没有任何 AT 消息。')
        return
    text = 'Here you are.'
    message_id = msg.get('mid')
    bot.sendMessage(chat_id=message.chat.id, reply_to_message_id=message_id, text=text)


Pic = Object.extend('Pic')

def pic(message):
    query = Query(Pic)
    pics = query.find()
    bolcks = [pic.get('pid') for pic in pics]
    base_url = 'http://7xqh4i.com1.z0.glb.clouddn.com/pic'
    pic_num = None
    size_of_images = 314 # 0~size_of_images
    while pic_num == None or str(pic_num) in bolcks:
        pic_num = random.randint(0, size_of_images)
    bot.sendPhoto(chat_id=message.chat.id,
                  photo=base_url + str(pic_num) + '.jpg',
                  caption=pic_num)


def delpic(message):
    cmd, text = parse_cmd_text(message.text)
    if text == None:
        bot.sendMessage(chat_id=message.chat.id, reply_to_message_id=message.message_id, text='Use /delpic <pic\'s num>')
        return
    query = Query(Pic)
    query.equal_to('pid', text)
    pics = query.find()
    if pics == None or len(pics) == 0:
        pic = Pic()
        pic.set('pid', text)
        pic.save()
    bot.sendMessage(chat_id=message.chat.id, reply_to_message_id=message.message_id, text='Successful')


def songci(message):
    cmd, text = parse_cmd_text(message.text)
    keyword = urllib2.quote(text)
    response = urllib2.urlopen(songci_api + keyword)
    data = json.loads(response.read())
    Songci = Object.extend('Songci')
    __songci = Songci()
    __songci.set('keyword', keyword)
    __songci.set('data', response.read())
    __songci.save()
    a_songci = data['result']['list'][0]
    __text = a_songci['title'] + '\n' + a_songci['author'] + '\n' + a_songci['content']
    bot.sendMessage(chat_id=message.chat.id, text=__text.replace('&nbsp;', ' '))
