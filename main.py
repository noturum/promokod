import requests

from bs4 import BeautifulSoup
from mysql.connector import connect, Error

from multiprocessing import Process
import telebot
from telebot import types
import random
bot = telebot.TeleBot("2113467244:AAFSOi8Dj1INRWLBEIuuFwuOqkwYhtJoHL0")
promokodo=[{'url':'https://www.promkod.ru/all-shops','classes':['offer-list-item','offer-list-item-title','offer-list-item-button_hidden-code'],'get':'data-code','listUrl':'https://www.promkod.ru/all-shops'},
{'url':'https://www.promokodo.ru','classes':['mer_cpon_list mer-box-mod ofhd code','cpon_word','coupon_code'],'get':None,'listUrl':'https://www.promokodo.ru/vse-magaziny'}]
class parcer():
    def __init__(self,parcers:list,target):
        self.parcers=parcers
        self.target=target
    def getListCode(self):
        HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko', 'accept': '*/*'}
        d = []

        list =[]
        out={}
        self.parcers=self.searchTarget(self.target)

        for parcer in self.parcers:
            if len(parcer['targets'])>0:
                for target in parcer['targets']:

                    if parcer['targets'][target].find('http')!=-1:
                        url = parcer['targets'][target]
                    else:
                        url=parcer['url']+'{}'.format(parcer['targets'][target])

                    response = requests.get(url, headers=HEADERS)
                    response.encoding = 'utf-8'

                    soup = BeautifulSoup(response.text, 'lxml')
                    objs=soup.findAll(attrs={'class':parcer['classes'][0]})

                    for obj in objs:

                        if not obj == None:
                            if obj.find(attrs={'class':parcer['classes'][1]})!=None and obj.find(attrs={'class': parcer['classes'][2]})!=None:
                                if parcer['get']==None:
                                    d=(obj.find(attrs={'class':parcer['classes'][1]}).text.strip(),obj.find(attrs={'class': parcer['classes'][2]}).text)
                                else:
                                    d = (obj.find(attrs={'class': parcer['classes'][1]}).text.strip(),
                                      obj.find(attrs={'class': parcer['classes'][2]}).get(parcer['get']))

                                list.append(d)
                    if len(list)==0:
                        continue
                    if target in out:
                        out[target+str(random.randint(0,9))] = list
                    else:
                        out[target]=list
                    list=[]

        if len(out)>0:
            return out
        else:
            return 'empty'
    def searchTarget(self,target):
        HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
                   'accept': '*/*'}
        out = []
        targets={}

        for parcer in self.parcers:
            response = requests.get(parcer['listUrl'], headers=HEADERS)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            objs = soup.findAll('a')

            for obj in objs:

                if not obj == None:
                    if obj.get('href').find(target) != -1:

                        targets[obj.text]=obj.get('href')
            parcer['targets']=targets

            out.append(parcer)
            targets={}

        return out
class proc(Process):
    def __init__(self,id,parcers,target):
        Process.__init__(self)
        self.id=id
        self.parcers=parcers
        self.target=target
    def start(self) -> None:
        fillkupon(self.id,self.parcers,self.target)
bigdata=None
def fillkupon(id,parcers,target):
    global bigdata,lastID
    data = parcer(parcers,target).getListCode()
    if isinstance(data,str) and data=='empty':

        data = parcer(parcers,target).getListCode()
        if isinstance(data, str) and data == 'empty':
            bot.send_message('Empty',id)
        else:
            bigdata=data
            keyboard = types.InlineKeyboardMarkup()
            for el in data:
                keyboard.add(types.InlineKeyboardButton(text=el, callback_data='target@{}'.format(el)))
            bot.send_message(id, "Shops:_________________________", reply_markup=keyboard)
    else:
        bigdata = data
        bot.delete_message(id,lastID)
        keyboard = types.InlineKeyboardMarkup()
        for el in data:
            keyboard.add(types.InlineKeyboardButton(text=el, callback_data='target@{}'.format(el)))
        bot.send_message(id, "Shops:_________________________", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.find('target')==0)
def target(call):
    for promo in bigdata[call.data.split('@')[1]]:
        bot.send_message(text=promo[0],chat_id=call.message.chat.id)
        bot.send_message(text=promo[1], chat_id=call.message.chat.id)

lastID=None
@bot.message_handler(commands=['start'])
def cmd(message):
    print(message)
    #bot.send_message('Hi!',message.chat.id)
@bot.message_handler(content_types=['text'])
def text(message):
    global lastID

    bot.delete_message(message.chat.id, message.id)
    lId=bot.send_message(text='Поиск...', chat_id=message.chat.id).id
    lastID = lId
    newProc=proc(message.chat.id,promokodo,message.text).start()


bot.polling()

