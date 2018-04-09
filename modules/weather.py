import forecastio
import datetime
from time import sleep
import requests
import json
from json import dumps
from keys import key

def timeConvert(miliTime):
    hours, minutes = miliTime.split(":")
    hours, minutes = int(hours), int(minutes)
    setting = " AM"
    if hours >= 12:
        if hours == 12:
            setting = " PM"
            hours = hours
        else:
            setting = " PM"
            hours -= 12
    if hours == 0:
        hours = 12
    return(("%02d:%02d" + setting) % (hours, minutes))

def Weather(conn):
    ip_url = 'https://freegeoip.net/json'
    request_zip = requests.get(ip_url)
    load_zip = json.loads(request_zip.text)

    lat = str(load_zip['latitude'])
    longs = str(load_zip['longitude'])
    API = key.api_keys['WEATHER_API']

    forecast = forecastio.manual('https://api.darksky.net/forecast/6a92bd8d0626c735970600815a0323a7/' + lat + ',' + longs + '')
    byHour = forecast.hourly()

    high_low = []
    for currentData in forecast.daily().data:
        high_low_list = []
        high_low_list.extend((currentData.temperatureLow, currentData.temperatureHigh))
        high_low.append(high_low_list)
    forecast_array = []
    high = str(int(round(high_low[0][1])))
    low = str(int(round(high_low[0][0])))
    #LOOP THROUGH HOURLY DATA
    for hourlyData in byHour.data:
        #CREATE ARRAY TO APPEND TO MASTER ARRAY
        forecast_array_list = []
        #GET TEMPERATURE TIME DATE AND SUMMARY
        temp = str(int(round(hourlyData.temperature)))
        time = hourlyData.time
        time = time - datetime.timedelta(hours=5)
        time = str(time).split()
        test_time = time[1]
        time_date = time[0]
        test_time = test_time[:-3]
        #CONVERT TIME TO STANDARD 12 HR TIME
        time = timeConvert(test_time)
        summary = hourlyData.summary
        #APPEND VARIABLES TO SINGLE ARRAY CREATED EARLIER AND THEN APPEND TO MASTER ARRAY FOR 2D ARRAY
        forecast_array_list.extend((temp,time,summary,time_date))
        forecast_array.append(forecast_array_list)

    #DELETE 25 ROWS AS WE DONT NEED ALL OF THEM
    #for i in range(25):
        #del forecast_array[-i]
    conn.send((forecast_array, high, low))
    conn.close()
    return(forecast_array, high, low)

#weather = weather()
#print(weather)

