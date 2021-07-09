import speech_recognition as sr
import pyttsx3
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import pickle
import urllib, requests
import json
import re
import time
import datetime

# Set up mic and tts voice
recognizer = sr.Recognizer()
microphone = sr.Microphone()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Pickle Global Constant Information
pickle_in = open('pickle', 'rb')
INFO = pickle.load(pickle_in)
print(INFO)

# Set up selenium
PATH = r"/Users/vincentruan/Desktop/Projects/chromedriver"
user_agent = '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
                AppleWebKit/537.36 (KHTML, like Gecko) 
                Chrome/90.0.4430.93 Safari/537.36'''

options = webdriver.ChromeOptions()
options.headless = True
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(PATH, options=options)

dt = datetime.datetime.now()
hour = dt.time().hour
minute = dt.time().minute
date = dt.date()


def take_command():
    with sr.Microphone() as source:
        print("Say something! ")
        recognizer.adjust_for_ambient_noise
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            command = command.lower()
            return command
        except:
            print('Unable to recognize speech')
            return False


def greeting():
    # ALARM CLOCK
    # while True:
    #     dt = datetime.datetime.now()
    #     hour = dt.time().hour
    #     minute = dt.time().minute
    #     if hour >= 5:
    #         break
    #     time.sleep(5)

    # INFO = {'date': dt.date()}
        
    # Update pickle INFO with dump
    INFO['date'] = date
    pickle_out = open('pickle', 'wb')
    pickle.dump(INFO, pickle_out)
    pickle_out.close()

    if hour < 12:
        time_of_day = "morning"
    elif hour >= 12 and hour < 18:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"
    
    clock_time = dt.strftime("%I:%M %p")

    weather = get_weather()

    if weather['high_tide'] != '':
        engine.say(f'''Good {time_of_day}. Today is {dt.date().strftime('%A, %B %d')}.
        It's {clock_time}, the weather in {weather['city']} is {weather['degrees']}
        degrees, with {weather['wind_speed']} wind speeds and {weather['skies']} skies.
        High tide will be at {weather['high_tide']}.''')
        engine.runAndWait()
    else:
        engine.say(f'''Good {time_of_day}. Today is {dt.date().strftime('%A %B %d')}.
        It's {clock_time}, the weather in {weather['city']} is {weather['degrees']}
        degrees, with {weather['wind_speed']} wind speeds and {weather['skies']} skies.''')
        engine.runAndWait()


def get_weather():
    res = requests.get('https://ipinfo.io')
    data = res.json()
    city = data['city']

    driver.get(f"https://www.google.com/search?q={city.replace(' ', '+').lower()}+weather")
    
    degrees = driver.find_element_by_id('wob_tm').text
    wind_speed = driver.find_element_by_id('wob_ws').text
    skies = driver.find_element_by_id('wob_dc').text

    search = driver.find_element_by_name('q')
    search.clear()
    search.send_keys(f"{city.lower()} high tide time")
    search.send_keys(Keys.RETURN)

    high_tide = driver.find_element_by_xpath('''//div[@id='rso']
        /div/div/div/div/div/div/div/div/div''').text

    weather = dict(
        city=city,
        degrees=degrees,
        wind_speed=wind_speed,
        skies=skies,
        high_tide=high_tide,
        )
    return weather


def play_song(song=0, id=0):
    import vlc
    import pafy

    
    def get_duration(video_id):
        API_KEY = "AIzaSyAVUXgjRmrf-yxdCkgg3kgl5MeB3_EN3us"

        search_url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=contentDetails'
        req = urllib.request.Request(search_url)
        response = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(response)
        all_data = data['items']
        duration = all_data[0]['contentDetails']['duration'][2:]
        print(duration)

        for i in range(3):
            try:
                # loop duration string, find first nonnumber
                int(duration[i])
            except:
                try:
                    hours = int(duration.split('H')[0])
                    duration = duration.split('H')[1]
                except:
                    hours = 0
                try:
                    minutes = int(duration.split('M')[0])
                    duration = duration.split('M')[1]
                except:
                    minutes = 0
                try:
                    seconds = int(duration.split('S')[0])
                except:
                    seconds = 0
                break

        print(f"H:{hours} M:{minutes} S:{seconds}")
        song_length = hours * 3600 + minutes * 60 + seconds
        print(song_length)
        return song_length

    # if passed in specific id to play
    if id != 0:
        url = "https://www.youtube.com/watch?v=" + id
        song_length = get_duration(id)

        # set up vlc player and play
        video = pafy.new(url)
        best = video.getbest()
        playurl = best.url

        Instance = vlc.Instance()
        player = Instance.media_player_new()
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        player.set_media(Media)
        player.audio_set_volume(70)
        player.play()

        # wait
        time.sleep(song_length - 2)
        return


    # get id of song from command
    search_input = song + " audio"
    query_string = urllib.parse.urlencode({"search_query" : search_input})
    html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    video_ids = re.findall(r"watch\?v=(\S{11})", html_content.read().decode('utf-8'))
    url = "https://www.youtube.com/watch?v=" + video_ids[0]
    print(video_ids[0])

    # get length of track
    video_id = video_ids[0]
    song_length = get_duration(video_id)

    # set up vlc player and play
    video = pafy.new(url)
    best = video.getbest()
    playurl = best.url

    Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new(playurl)
    Media.get_mrl()
    player.set_media(Media)
    player.audio_set_volume(70)
    player.play()

    # wait
    time.sleep(song_length - 2)


def play_my_spotify_playlist():
    import vlc
    import pafy

    import urllib
    import json
    import re

    import time
    import random

    import spotipy  
    from spotipy.oauth2 import SpotifyClientCredentials


    client_id = "4ad4f6e66123415ab7ed8afcbb7c9e9f"
    client_secret = "d835755caf614909baaa2742810a2cff"

    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


    def get_playlist_tracks(username,playlist_id):
        results = sp.user_playlist_tracks(username,playlist_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        return tracks


    def get_track_ids(user, playlist_id):
        tracks = get_playlist_tracks(user, playlist_id)
        ids = []
        for i in range(len(tracks)):
            ids.append(tracks[i].get('track').get('id'))
        return ids


    def get_track_features(id):
        meta = sp.track(id)
        features = sp.audio_features(id)

        # meta
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        release_date = meta['album']['release_date']
        length = meta['duration_ms']
        popularity = meta['popularity']

        # features
        acousticness = features[0]['acousticness']
        danceability = features[0]['danceability']
        energy = features[0]['energy']
        instrumentalness = features[0]['instrumentalness']
        liveness = features[0]['liveness']
        loudness = features[0]['loudness']
        speechiness = features[0]['speechiness']
        tempo = features[0]['tempo']
        time_signature = features[0]['time_signature']

        track = [name, album, artist, release_date, length, popularity, danceability, acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness, tempo, time_signature]
        return track


    ids = get_track_ids('yellowazns123', '073fl28tczQe04P8666m8Z')

    while True:

        #get random song_id from playlist, remove from list
        song_id = random.choice(ids)
        ids.remove(song_id)
        song = get_track_features(song_id)
        track_name = song[0]
        artist = song[2]
        print(f"Track: {track_name}")
        print(f"Artist: {artist}")

        search_input = f"{track_name} {artist} audio"
        print(search_input)
        query_string = urllib.parse.urlencode({"search_query" : search_input})
        html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
        video_ids = re.findall(r"watch\?v=(\S{11})", html_content.read().decode('utf-8'))
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
        print(video_ids[0])

        #play song
        video = pafy.new(url)
        best = video.getbest()
        playurl = best.url

        Instance = vlc.Instance()
        player = Instance.media_player_new()
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        player.set_media(Media)
        player.audio_set_volume(70)
        player.play()

        #get length of track
        video_id = video_ids[0]
        API_KEY = "AIzaSyAVUXgjRmrf-yxdCkgg3kgl5MeB3_EN3us"
        
        search_url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=contentDetails'
        req = urllib.request.Request(search_url)
        response = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(response)
        all_data = data['items']
        duration = all_data[0]['contentDetails']['duration']
        print(duration)
        minutes = int(duration[2:].split('M')[0])
        seconds = duration[2:].split('M')[1].split('S')[0]
        if seconds == '':
            seconds = 0
        else:
            seconds = int(seconds)
        song_length = minutes * 60 + seconds
        print(song_length)

        #wait, repeat
        time.sleep(song_length - 2)


def search_video(command):
    search_input = command.partition('search ')[2]
    query_string = urllib.parse.urlencode({"search_query" : search_input})
    engine.say('searching ' + search_input)
    engine.runAndWait()
    webbrowser.open('https://youtube.com/results?' + query_string)
    html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    video_ids = re.findall(r"watch\?v=(\S{11})", html_content.read().decode('utf-8'))
    return video_ids


def play_video(command, video_ids):
    from fuzzywuzzy import fuzz
    API_KEY = "AIzaSyAVUXgjRmrf-yxdCkgg3kgl5MeB3_EN3us"

    high = 0
    id = ''
    for i in range(int(len(video_ids) / 2)):
        search_url = f'https://www.googleapis.com/youtube/v3/videos?id={video_ids[i]}&key={API_KEY}&part=snippet'
        req = urllib.request.Request(search_url)
        response = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(response)
        title = data['items'][0]['snippet']['title'].lower()
        fuzz_ratio = fuzz.WRatio(command, title)
        if fuzz_ratio > high:
            high = fuzz_ratio
            id = video_ids[i]

    webbrowser.open('https://www.youtube.com/watch?v=' + id)

# def define_word(command):
#     if ("what is " in command or "definition of " in command) and "mean" not in command.split()[-1]:
#         word = command.split()[-1]
#     elif "what does " in command and "mean" in command.split()[-1] or " definition" or " meaning" in command:
#         word = command.split()[-2]

#     driver.get(f"https://www.google.com/search?q={word}+definition")
#     try:
#         definition = driver.find_element_by_xpath('''//div[@jscontroller='PWuiIf']
#         /div/div[3]/div/div[4]/div/div/ol/li/div/div/div/div/div/div/span''')
#         print('first')
#     except:
#         try:
#             definition = driver.find_element_by_xpath('''//span[@class = "hgKElc"]''')
#             print('second')
#         except:
#             print('third')
#     try:
#         print(definition.text)
#     except:
#         pass
#     try:
#         return definition.text, word, True
#     except:
#         return False, False, False


def run():
    if INFO['date'] != date:
        greeting()
    while True:
        command = take_command()
        print(command)
        if command is False:
            continue
        elif 'greeting' in command:
            greeting()
        elif command == 'what it do baby':
            engine.say('What it do baby!')
            engine.runAndWait()
        elif 'i am back' in command:
            play_song(id='OkLPGrjInyA')
        
        elif 'play spotify' in command or ('play ' in command and 'spotify' in command
        and 'playlist' in command):
            play_my_spotify_playlist()
        elif 'play ' in command:
            song = command.partition('play ')[2]
            print('playing ' + song)
            engine.say('playing' + song)
            engine.runAndWait()
            play_song(song)
        elif 'open youtube' in command:
            engine.say('opening youtube')
            engine.runAndWait()
            webbrowser.open('https://youtube.com')
            while True:
                command = take_command()
                print(command)
                if command is False:
                    continue
                if 'search' in command:
                    video_ids = search_video(command)
                    break
            while True:
                command = take_command()
                print(command)
                if command is not False:
                    play_video(command, video_ids)
                    break


run()