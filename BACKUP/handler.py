from modules import news
from modules import weather
from modules import youtube
from modules import sms
from modules import timers
from modules import define
from keys import key
from multiprocessing import Process, Pipe
import time
import paho.mqtt.client as mqtt
import requests
import json
import datetime
import os


############################################

mqtt_client = mqtt.Client()
HOST = key.mqtt_keys[0]
PORT = int(key.mqtt_keys[1])
TOPICS = key.mqtt_topics
timer = None
#API KEYS
YOUTUBE_API = key.api_keys['YOUTUBE_API']
WEATHER_API = key.api_keys['WEATHER_API']
YANDEX_API = key.api_keys['YANDEX_API']

############################################

def on_connect(client, userdata, flags, rc):
    for topic in TOPICS:
        mqtt_client.subscribe(topic)

############################################

def playVideo(query):
    youtube_process = Process(target = youtube.Youtube, args = [query,])
    youtube_process.start()

def getNews():
    p_conn, c_conn = Pipe()
    news_process = Process(target = news.News, args=(c_conn,))
    news_process.start()
    return(p_conn.recv())

def sendArticles(articles):
    news = []
    for article in articles:
        artcle = []
        author = article['author']
        if author is not None:
            if 'http' in author:
                author = 'No author'
            if author == "":
                author = 'No author'
        if author is None:
            author = 'No author'
        description = article['description']
        title = article['title']
        url = article['url']
        name = article['source']['name']
        artcle.extend((author, name, title, description, url))
        news.append(artcle)
    send = sms.Messenger()
    message = "Hey Nick!\n Here are some current articles: \n \n {0} by {1} {2} \n \n {3} by {4} {5} \n \n {6} by {7} {8} \n \n {9} by {10} {11} \n \n {12} by {13} {14} \n \n ".format(
        news[0][2],news[0][1], news[0][4],
        news[1][2],news[1][1], news[1][4],
        news[2][2],news[2][1], news[2][4],
        news[3][2],news[3][1], news[3][4],
        news[4][2],news[4][1], news[4][4]
        )
    send.body = message
    send.send_sms()
    news_array = [news[0][2], news[0][0]]
    return news_array

def getWeather():
    p_conn, c_conn = Pipe()
    weather_process = Process(target = weather.Weather, args=(c_conn,))
    weather_process.start()
    return(p_conn.recv())

def timedate():
    import datetime
    time = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    return str("Currently it is {0}".format(time))
#############################################


def on_message(client, userdata, msg):
    global timer
    if msg.topic not in TOPICS:
        return False
    os.system('aplay /home/pi/snips-custom-hotword/resources/dong.wav')
    slots = parse_slots(msg)
    #print(str(slots))

    if msg.topic == 'hermes/intent/searchWeatherForecast':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/searchWeatherForecastCondition':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/searchWeatherForecastItem':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/searchWeatherForecastTemperature':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/playPlaylist':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/playAlbum':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/speakerInterrupt':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/nextSong':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/volumeDown':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/resumeMusic':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/previousSong':
        response = 'it worked! {0}'.format(msg.topic)
    elif msg.topic == 'hermes/intent/radioOn':
        response = 'Turning the radio on!'
    elif msg.topic == 'hermes/intent/playArtist':
        query = slots.get("artist_name", None) + ' top tracks'
        youtube = playVideo(query)
        response = 'Playing top tracks by {1}'.format(msg.topic, slots.get("artist_name", None))
    elif msg.topic == 'hermes/intent/volumeUp':
        response = 'Turning volume up!'
    elif msg.topic == 'hermes/intent/nickdeb:playSong':
        youtube = playVideo(slots.get("song_name", None))
        response = 'Playing {0} for you'.format(slots.get("song_name", None))
    elif msg.topic == 'hermes/intent/Odia_home:TellTimeDate':
        time = timedate()
        response = time
    elif msg.topic == 'hermes/intent/nickdeb:defineWord':
        words = define.Define(slots.get("define", None))
        sentence = ""
        if words:
            for word in words:
                if word == words[0]:
                    sentence = sentence + "The first definition is {0}".format(word)
                else:
                    sentence = sentence + ". Another definition is {0}".format(word)
        response = sentence
    elif msg.topic == 'hermes/intent/AcidFlow:StopTimer':
        timer.cancel()
        response = 'Stopping the timer!'
    elif msg.topic == 'hermes/intent/nickdeb:SetTimer':
        time = slots.get("timer_duration", None)
        time = time.split(" ")
        timer = timers.Timers(time[0], time[1])
        timer.start()
        response = 'Setting a timer for {0}!'.format(slots.get("timer_duration", None))
    elif msg.topic == 'hermes/intent/nickdeb:getNews':
        news = getNews()
        news = sendArticles(news)
        response = 'I have sent you the top articles on your phone! Right now, the top article is {0} by {1}'.format(news[0], news[1])

    print(response)
    session_id = parse_session_id(msg)
    say(session_id, response)







#############################################
def parse_slots(msg):
    data = json.loads(msg.payload.decode())
    return {slot['slotName']: slot['rawValue'] for slot in data['slots']}


def parse_session_id(msg):
    data = json.loads(msg.payload.decode())
    return data['sessionId']


def say(session_id, text):
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({'text': text, "sessionId" : session_id}))


#############################################


if __name__ == '__main__':
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(HOST, PORT)
    mqtt_client.loop_forever()
