from __future__ import unicode_literals
import subprocess
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import urllib, json, sys
from six import string_types
from signal import pause
from omxplayer.player import OMXPlayer
from gpiozero import Button
import sys
from multiprocessing import Process
from keys import key

button_pause = Button(17)
button_quit = Button(2)
button_skip = Button(3)
var_pause = False
var_skip = False
var_quit = False

DEVELOPER_KEY = key.api_keys['YOUTUBE_API']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

'''

OMXPLAYER

'''

class Player:

    def __init__(self, url):
        self.url = url
        self.player = None
        self.state = True
        self.playlist = False
        self._play = True

    def start(self):
        if isinstance(self.url, string_types):
            cmd = 'youtube-dl -g -f best {0}'.format(self.url)
            yt_dl = subprocess.Popen(cmd,shell=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (url, err) = yt_dl.communicate()
            if yt_dl.returncode != 0:
                sys.stderr.write(err)
                print('error')
            yurl = url.decode('UTF-8').strip()
            self.player = OMXPlayer(yurl, args=['-o','hdmi'])
            return self.player.duration()

    def stop(self):
        self.player.stop()
        self._play = False
        self.player = None
        return False

    def skip(self):
        if self.playlist == True:
            self.player.stop()
            return True
        else:
            self.player.stop()
            return False

    def toggle(self):
        #false = not playing // true = playing
        if self.state == True:
            self.state = False
            self.player.pause()
        elif self.state == False:
            self.state = True
            self.player.play()
        else:
            return False

    def is_play(self):
        return self.player.can_control()






class Handlers:

    def __init__(self):
        self.url = None
        self.typeof = None
        self.proc = None
        self._play = True
        self.player = None
        self.players = None

    def input_handler(self):
        if self.typeof == 'video':
            #print(url)
            self.players = [Player(self.url)]
            self.player = self.players[0]
            print('url for video:: {0}'.format(self.player.url))
            self.player.start()
            #self.proc = Process(target = self.output_handler)
            #self.proc.start
            self.output_handler()
        elif self.typeof == 'playlist':
            for video in self.url:
                if self._play == True:
                    print(self._play)
                    #print(video)
                    self.players = [Player(video)]
                    self.player = self.players[0]
                    print('url for playlist video:: {0}'.format(self.player.url))
                    self.player.playlist = True
                    self.player.start()
                    #self.proc = Process(target = self.output_handler)
                    #self.proc.start()
                    self.output_handler()
                else:
                    return False

    def output_handler(self):
        global button_quit
        global button_pause
        global button_skip
        global var_quit
        global var_pause
        global var_skip
        if self._play == True:
            #player.start()
            time.sleep(2.5)
            p = self.player
            p.playlist = True
            if p is not None:
                try:
                    while p.is_play():
                        if self._play == True:
                            if button_quit.is_pressed:
                                p.stop()
                                self._play = False
                                return False
                            elif button_pause.is_pressed:
                                p.toggle()
                                time.sleep(1)
                            elif button_skip.is_pressed:
                                if p.playlist == True:
                                    p.skip()
                                    return True
                                else:
                                    p.stop()
                                    return False
                                time.sleep(1)
                            
                            elif var_skip == True:
                                var_skip = False
                                if p.playlist == True:
                                    p.skip()
                                    return True
                                else:
                                    p.stop()
                                    return False
                                time.sleep(1)
                            elif var_quit == True:
                                p.stop()
                                self._play = False
                                var_quit = False
                                return False
                            elif var_pause == True:
                                print('pausing')
                                p.toggle()
                                time.sleep(1)
                                var_pause = False
                            
                            else:
                                time.sleep(0.1)
                                print(var_pause, var_quit, var_skip)
                                global var_quit
                                global var_pause
                                global var_skip
                                p.is_play()
                        else:
                            print('not playable')
                            return False
                except Exception as e:
                    print("Something went wrong. Here it is: {0}".format(e))



'''

VIDEO HANDLERS

'''





def video_handler(typeof, vid):
    #print(typeof, vid)
    if typeof == 'video':
        url = 'https://www.youtube.com/watch?v={0}'.format(vid)
        handler = Handlers()
        handler.url = url
        handler.typeof = 'video'
        handler.input_handler()
        #script continues once video is killed here
    elif typeof == 'playlist':
        videos = []
        url = "https://www.youtube.com/playlist?list={0}".format(vid)
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
        # Retrieve the list of videos uploaded to the authenticated user's channel.
        playlistitems_list_request = youtube.playlistItems().list(playlistId=vid, part='snippet', maxResults=25)
        while playlistitems_list_request:
          playlistitems_list_response = playlistitems_list_request.execute()
        # Print information about each video.
          for playlist_item in playlistitems_list_response['items']:
            title = playlist_item['snippet']['title']
            video_id = playlist_item['snippet']['resourceId']['videoId']
            videos.append('https://www.youtube.com/watch?v=%s' % (video_id))

          playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)
        if len(videos) > 25:
            videos = videos[:25]

        handler = Handlers()
        handler.url = videos
        handler.typeof = 'playlist'
        handler.input_handler()

    else:
        return 'Something went wrong'



'''

Searching youtube for results

'''
def Youtube(query):
      #build youtube endpoint
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

      #Search for youtube

    search_response = youtube.search().list(
      q=query,
      part='id,snippet',
      maxResults='5'
    ).execute()

    #Create empty placeholders
    videos = []
    playlists = []
    channels = []
    #loop through response and append appropiate objects
    for search_result in search_response.get('items', []):
      if search_result['id']['kind'] == 'youtube#video':
        videos.append('%s' % (search_result['id']['videoId']))
      elif search_result['id']['kind'] == 'youtube#channel':
        channels.append('%s' % (search_result['id']['channelId']))
      elif search_result['id']['kind'] == 'youtube#playlist':
        playlists.append('%s' % (search_result['id']['playlistId']))

        #Call correct typeof in videohandler and pass in video ids
    if videos:
       video_handler('video', videos[0])
    elif playlists:
       video_handler('playlist', playlists[0])
    elif channels:
       return 'Unsuccessful, try a different word'




