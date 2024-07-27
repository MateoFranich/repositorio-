import telebot
from pytrends.request import TrendReq
import snscrape.modules.twitter as sntwitter
import logging
import certifi
import os
import ssl
import urllib3

def update_certificates():
    cafile = certifi.where()
    os.environ['SSL_CERT_FILE'] = cafile
    os.environ['SSL_CERT_DIR'] = os.path.dirname(cafile)
    ssl._create_default_https_context = ssl.create_default_context

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

update_certificates()

API_TOKEN = '7433787803:AAFuedeOGqjVSN5bc1TSYTrBLlc4pO2fe0E'
bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(level=logging.INFO)

def get_google_trends():
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        trending_searches_df = pytrends.trending_searches()
        trends = trending_searches_df[0].tolist()
        return trends
    except Exception as e:
        logging.error(f"Error al obtener tendencias de Google: {e}")
        return []

def get_twitter_trends():
    try:
        trends_list = []
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper('trending').get_items()):
            if i >= 10:  
                break
            trends_list.append(tweet.content)
        return trends_list
    except Exception as e:
        logging.error(f"Error al obtener tendencias de Twitter: {e}")
        return []

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hola, soy tu asistente personal.")

@bot.message_handler(commands=['trends'])
def send_trends(message):
    google_trends = get_google_trends()
    twitter_trends = get_twitter_trends()
    response = "Tendencias de Google:\n" + "\n".join(google_trends[:5]) + "\n\nTendencias de Twitter:\n" + "\n".join(twitter_trends[:5])
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()
