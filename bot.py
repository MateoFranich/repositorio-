import telebot
from telebot import types
from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
import logging
from collections import Counter
import certifi
import os
import ssl

def update_certificates():
    # Ruta al archivo cacert.pem de certifi
    cafile = certifi.where()

    os.environ['SSL_CERT_FILE'] = cafile
    os.environ['SSL_CERT_DIR'] = os.path.dirname(cafile)

    ssl._create_default_https_context = ssl.create_default_context

update_certificates()

API_TOKEN = '7433787803:AAFuedeOGqjVSN5bc1TSYTrBLlc4pO2fe0E'
bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(level=logging.INFO)

def get_google_trends(region='world'):
    try:
        pytrends = TrendReq(hl='es-AR', tz=360)
        if region == 'argentina':
            trending_searches_df = pytrends.trending_searches(pn='argentina')
        else:
            trending_searches_df = pytrends.trending_searches()
        trends = trending_searches_df[0].tolist()
        return trends
    except Exception as e:
        logging.error(f"Error al obtener tendencias de Google: {e}")
        return []

def get_twitter_trends(location='argentina'):
    try:
        url = f'https://trends24.in/{location}/'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        trends_list = []

        trend_cards = soup.find_all('ol', class_='trend-card__list')
        if not trend_cards:
            logging.error("No se encontraron tarjetas de tendencias.")
            return trends_list

        trends = trend_cards[0].find_all('li')
        for trend in trends:
            trends_list.append(trend.text.strip())

        return trends_list[:10]
    except Exception as e:
        logging.error(f"Error al obtener tendencias de Twitter de {location}: {e}")
        return []

def get_recent_tweets():
    try:
        url = 'https://api.twitter.com/2/tweets/search/recent'
        params = {
            'query': '#',  
            'max_results': 100,
            'tweet.fields': 'entities'
        }
        headers = {
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAAM2FuwEAAAAAYUQHNqeJzyr6kNHlB%2BJXUGe35Ao%3DUQWHok1vNWgNJLIInYLakkTjzz6T48qV4b7E1Rggn0YDSQzWPK' 
        }
        response = requests.get(url, headers=headers, params=params)
        tweets = response.json()
        hashtags = []
        for tweet in tweets['data']:
            if 'entities' in tweet and 'hashtags' in tweet['entities']:
                for hashtag in tweet['entities']['hashtags']:
                    hashtags.append(hashtag['tag'])
        return [tag for tag, count in Counter(hashtags).most_common(10)]
    except Exception as e:
        logging.error(f"Error al obtener tweets recientes: {e}")
        return []

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hola, soy tu asistente personal.")
    show_keyboard(message)

@bot.message_handler(commands=['trends'])
def send_trends(message):
    google_trends_global = get_google_trends()
    google_trends_arg = get_google_trends('argentina')
    twitter_trends_arg = get_twitter_trends('argentina')
    twitter_trends_global = get_twitter_trends('') 
    
    response = ("Tendencias de Google Globales:\n" + "\n".join(google_trends_global[:5]) +
                "\n\nTendencias de Google en Argentina:\n" + "\n".join(google_trends_arg[:5]) +
                "\n\nTendencias de Twitter en Argentina:\n" + "\n".join(twitter_trends_arg[:5]) +
                "\n\nTendencias de Twitter Globales:\n" + "\n".join(twitter_trends_global[:5]))
    bot.reply_to(message, response)

def show_keyboard(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('/start')
    itembtn2 = types.KeyboardButton('/help')
    itembtn3 = types.KeyboardButton('/trends')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Elige un comando:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    show_keyboard(message)
    bot.reply_to(message, message.text)

bot.polling()
