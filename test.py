import speech_recognition as sr
import pyttsx3
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import vlc
import pafy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pickle
import urllib, requests
from fuzzywuzzy import fuzz
import json
import re
import time
import random
import datetime

# Set up mic and tts voice
recognizer = sr.Recognizer()
microphone = sr.Microphone()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Pickle Global Constant Information from Pickle File
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
clock_time = dt.strftime("%I:%M %p")


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


def alarm_clock(wakeup_hour, wakeup_minute):
    # ALARM CLOCK
    print(f'Alarm at {wakeup_hour}:{wakeup_minute}')
    while True:
        dt = datetime.datetime.now()
        hour = dt.time().hour
        minute = dt.time().minute
        # print(f'{hour}:{minute}')
        if hour == wakeup_hour and minute >= wakeup_minute:
            play_song(id='qPaM3_oPk-A')
            break
        time.sleep(5)


def greeting():
    # # ALARM CLOCK
    # while True:
    #     dt = datetime.datetime.now()
    #     hour = dt.time().hour
    #     minute = dt.time().minute
    #     if hour >= 5:
    #         break
    #     time.sleep(5)

    INFO = {'date': dt.date()}
        
    # Update pickle INFO with dump
    INFO['date_today'] = date
    pickle_out = open('pickle', 'wb')
    pickle.dump(INFO, pickle_out)
    pickle_out.close()

    if hour < 12:
        time_of_day = "morning"
    elif hour >= 12 and hour < 18:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

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

    high_tide = ''
    # Get tide time from Google
    try:
        high_tide = driver.find_element_by_xpath('''//div[@id='rso']
            /div/div/div/div/div/div/div/div/div''').text
        # If gotten correct time
        if ':' in high_tide and ('am' in high_tide or 'pm' in high_tide):
            print(high_tide)
        else:
            print('NOT HIGH TIDE TIME')
            # If Google gives 'tide-forecast output, find tide time
            try:
                high_tide = driver.find_element_by_xpath('''/html/body/div[7]/div/div[8]/
                div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div[1]/div/div[1]/
                div/div[2]/table/tbody/tr[4]/td[2]/b''').text
                print(high_tide)
            except:
                try:
                    high_tide = driver.find_element_by_xpath('''/html/body/div[7]/div/
                    div[9]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div[1]/
                    div/div[1]/div/div[2]/table/tbody/tr[4]/td[2]/b''').text
                    print(high_tide)
                except:
                    try:
                        high_tide = driver.find_element_by_xpath('''/html/body/div[7]/div/
                        div[10]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div[1]/
                        div/div[1]/div/div[2]/table/tbody/tr[4]/td[2]/b''').text
                        print(high_tide)
                    except:
                        try:
                            high_tide = driver.find_element_by_xpath('''/html/body/div[7]/
                            div/div[8]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/
                            div/div[1]/div/div[1]/div/div[2]/table/tbody/tr[5]/td[2]/b''').text
                            print(high_tide)
                        except:
                            try:
                                high_tide = driver.find_element_by_xpath('''/html/body/div[7]/div/
                                div[9]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div[1]
                                /div/div[1]/div/div[2]/table/tbody/tr[5]/td[2]/b''').text
                            except:
                                print('FAILED')
                                high_tide = ''
                                pass
    except:
        # If none, return empty tide time
        pass

    # # If Google gives 'tide-forecast output, find tide time
    # if ':' not in high_tide or ('am' not in high_tide and 'pm' not in high_tide) and '''Today's tide times for''' in high_tide:
    #     try:
    #         high_tide = driver.find_element_by_xpath('''/html/body/div[7]/div/div[8]/
    #         div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div[1]/div/div[1]/
    #         div/div[2]/table/tbody/tr[4]/td[2]/b''').text
    #         print(high_tide)
    #     except:
    #         try:
    #             high_tide = driver.find_element_by_xpath('''/html/body/div[7]/div/
    #             div[9]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div[1]/
    #             div/div[1]/div/div[2]/table/tbody/tr[4]/td[2]/b''').text
    #             print(high_tide)
    #         except:
    #             try:
    #                 high_tide = driver.find_element_by_xpath('''/html/body/div[7]/div/
    #                 div[10]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div[1]/
    #                 div/div[1]/div/div[2]/table/tbody/tr[4]/td[2]/b''').text
    #                 print(high_tide)
    #             except:
    #                 pass
        
    weather = dict(
        city=city,
        degrees=degrees,
        wind_speed=wind_speed,
        skies=skies,
        high_tide=high_tide,
        )
    return weather


def play_song(song=0, id=0):
    
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
        time.sleep(song_length)
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
    time.sleep(song_length)


def play_my_spotify_playlist(id=0):
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


    ids = get_track_ids('yellowazns123', id)

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
        time.sleep(song_length)


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


def get_emails(email_command=''):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    emails = INFO['emails']
    print(emails)

    # If user requesting specific email
    if email_command != '':
        # Find matching intended email
        high = 0
        email = ''
        for i in emails:
            fuzz_ratio = fuzz.WRatio(email_command, i)
            print(f'{i} : {fuzz_ratio}')
            # Get email with higher fuzz score
            if fuzz_ratio > high:
                high = fuzz_ratio
                email = i
            elif fuzz_ratio == high:
                # If fuzz score same, get email with shorter length
                if len(i) < len(email):
                    email = i

        if high < 65:
            # Email does not match, exit
            print('Invalid email')
            engine.say('Invalid email')
            engine.runAndWait()
            return
        else:
            # Get Emails from individual email account
            print(email)

            # Get Credentials
            creds = None
            # If JSON email file exists, get creds
            if os.path.exists(f'{email}.json'):
                creds = Credentials.from_authorized_user_file(f'{email}.json', SCOPES)
            # If no credentials available or invalid, set up log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    # If creds expired/invalid
                    print(f'{email} expired')
                    creds.refresh(Request())
                else:
                    # No creds, automate it
                    print(f'{email} creds invalid')
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save credentials to json file
                with open(f'{email}.json', 'w') as token:
                    token.write(creds.to_json())

            service = build('gmail', 'v1', credentials=creds)

            # Get Messages
            results = service.users().messages().list(userId='me', labelIds = ['INBOX'],
                q='is:unread').execute()
            messages = results.get('messages', [])

            message_count = 0
            if not messages:
                # No messages
                print(f'{email} has no new emails')
                engine.say(f'{email} has no new emails')
                engine.runAndWait()
                return
            else:
                # Tell user number of emails
                message_count = len(messages)
                # Has unread messages
                if message_count == 1:
                    print(f'{email} has 1 new email')
                    engine.say(f'{email} has one new email')
                    engine.runAndWait()
                else:
                    print(f'{email} has {message_count} new emails')
                    engine.say(f'{email} has {message_count} new emails')
                    engine.runAndWait()
            
             # Print emails
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email_data = msg['payload']['headers']
                for values in email_data:
                    name = values['name']
                    if name == 'From':
                        from_name = values['value']
                        print(f'You have a new email from {from_name}:')
                        print(f'''    {msg['snippet']}...''')
                        print('\n')

    else:
        # Get all emails from all emails
        # Initialize unread dict for each email
        unread_status = {}
        for email in emails:
            unread_status[email] = 'read'

        unread = False
        message_count = 0
        # Print emails and email count
        for email in emails:
            # Get Credentials
            creds = None
            # If JSON email file exists, get creds
            if os.path.exists(f'{email}.json'):
                creds = Credentials.from_authorized_user_file(f'{email}.json', SCOPES)
            # If no credentials available or invalid, set up log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    # If creds expired/invalid
                    print(f'{email} expired')
                    creds.refresh(Request())
                else:
                    # No creds, automate it
                    print(f'{email} creds invalid')
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save credentials to json file
                with open(f'{email}.json', 'w') as token:
                    token.write(creds.to_json())

            service = build('gmail', 'v1', credentials=creds)

            # Get Messages
            results = service.users().messages().list(userId='me', labelIds = ['INBOX'],
                q='is:unread').execute()
            messages = results.get('messages', [])

            if not messages:
                print(f'{email} has no new emails')
            else:
                # Tell user number of emails, show if requested
                # Has unread messages
                unread = True
                unread_status[email] = 'unread'
                message_count += len(messages)
                if len(messages) == 1:
                    print(f'{email} has 1 new email')
                else:
                    print(f'{email} has {len(messages)} new emails')

        if not unread:
            engine.say('You have no new emails!')
            engine.runAndWait()
            return
        
        if message_count == 1:
            engine.say(f'You have {message_count} total new email')
            engine.runAndWait()
        else:
            engine.say(f'You have {message_count} total new emails')
            engine.runAndWait()
        
        for email in emails:
            # Get emails for each email with messages
            if unread_status[email] == 'unread':
                engine.say(f'Getting emails from {email}')
                engine.runAndWait()

            # Get Credentials
            creds = None
            if os.path.exists(f'{email}.json'):
                creds = Credentials.from_authorized_user_file(f'{email}.json', SCOPES)
            # If no credentials available, let user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save credentials to json file
                with open(f'{email}.json', 'w') as token:
                    token.write(creds.to_json())

            service = build('gmail', 'v1', credentials=creds)

            # Get Messages
            results = service.users().messages().list(userId='me', labelIds = ['INBOX'],
                q='is:unread').execute()
            messages = results.get('messages', [])

            # Print emails
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                email_data = msg['payload']['headers']
                for values in email_data:
                    name = values['name']
                    if name == 'From':
                        from_name = values['value']
                        print(f'You have a new email from {from_name}:')
                        print(f'''    {msg['snippet']}...''')
                        print('\n')



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
    if INFO['date_today'] != date:
    # alarm_clock(19, 0)
        greeting()
    while True:
        command = take_command()
        print(command)
        if command is False:
            continue
        elif 'greeting' in command:
            greeting()
        elif command == 'what it do baby':
            play_song(id='kq4iy8K79ew')
        elif 'i am back' in command:
            play_song(id='OkLPGrjInyA')
        
        # play EDM spotify playlist
        elif ('play spotify' in command and 'edm' in command) or ('play ' in command
        and 'edm' in command and 'playlist' in command):
            engine.say('playing your EDM spotify playlist')
            engine.runAndWait()
            play_my_spotify_playlist('2x02jcUK9zbZg7r72Y0LTK')
        # play other spotify playlist
        elif 'play spotify' in command or ('play ' in command and 'spotify' in command
        and 'playlist' in command):
            engine.say('playing spotify')
            engine.runAndWait()
            play_my_spotify_playlist('073fl28tczQe04P8666m8Z')
        elif 'play ' in command:
            song = command.partition('play ')[2]
            print('playing ' + song)
            engine.say('playing' + song)
            engine.runAndWait()
            play_song(song)
        elif 'email' in command or 'emails' in command or 'gmail' in command:
            if ' from ' in command:
                # Parse email in speech text
                email_command = command.partition(' from ')[2]
                # Get email count and email content
                get_emails(email_command)
                continue
            elif 'does ' in command and (' has ' in command or ' have ' in command):
                # Parse email in speech text
                email_command = re.search('does (.*) have', command)
                # Get email count and email content
                get_emails(email_command)
                continue
            
            # If no email specified, get emails of all emails
            get_emails()

        # NOT VERY GOOD, NEEDS WORK
        # elif 'open youtube' in command:
        #     engine.say('opening youtube')
        #     engine.runAndWait()
        #     webbrowser.open('https://youtube.com')
        #     while True:
        #         command = take_command()
        #         print(command)
        #         if command is False:
        #             continue
        #         if 'search' in command:
        #             video_ids = search_video(command)
        #             break
        #     while True:
        #         command = take_command()
        #         print(command)
        #         if command is not False:
        #             play_video(command, video_ids)
        #             break

run()