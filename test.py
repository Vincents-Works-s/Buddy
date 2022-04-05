from __future__ import print_function

import speech_recognition as sr
import pyttsx3
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
import pytz

# Set up mic and tts voice
recognizer = sr.Recognizer()
microphone = sr.Microphone()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Pickle Global Constant Information from Pickle File
pickle_in = open('pickle_info', 'rb')
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

# Get date information
dt = datetime.datetime.now()
hour = dt.time().hour
minute = dt.time().minute
date = dt.date()
clock_time = dt.strftime("%I:%M %p")

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_EXTENSIONS = ['rd', 'th', 'st', 'nd']


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
    # Get date information REPEATING
    dt = datetime.datetime.now()
    hour = dt.time().hour
    minute = dt.time().minute
    date = dt.date()
    clock_time = dt.strftime("%I:%M %p")
    
    # Update pickle INFO with dump
    INFO['date_last_opened'] = date
    INFO['date_today'] = date
    pickle_out = open('pickle_info', 'wb')
    pickle.dump(INFO, pickle_out)
    pickle_out.close()

    if hour < 12:
        time_of_day = "morning"
    elif hour >= 12 and hour < 18:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

    weather = get_weather()
    print(weather)

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
    # # Get the city of current location - IPINFO.IO
    # res = requests.get('https://ipinfo.io')
    # data = res.json()
    # city = data['city']
    
    # GET CITY WITH GET.GEOJS
    r = requests.get('https://get.geojs.io/')

    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    ip_add = ip_request.json()['ip']

    url = 'https://get.geojs.io/v1/ip/geo/' + ip_add + '.json'
    geo_request = requests.get(url)
    geo_data = geo_request.json()
    city = geo_data['city']
    print(geo_data)

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
        high_tide = driver.find_element_by_xpath('''/html/body/div[7]/div/div[9]/div[1]/
        div/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div[1]/div/div/div/div/div[1]/
        div/div[1]/div''').text
        # high_tide = driver.find_element_by_xpath('''//div[@id='rso']
        #     /div/div/div/div/div/div/div/div/div''').text

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
        
    weather = dict(
        city=city,
        degrees=degrees,
        wind_speed=wind_speed,
        skies=skies,
        high_tide=high_tide,
        )
    return weather

#HERE
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
        best = video.getbestaudio()
        playurl = best.url

        Instance = vlc.Instance()
        player = Instance.media_player_new()
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        player.set_media(Media)
        player.audio_set_volume(80)
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

#HERE
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
        best = video.getbestaudio()
        playurl = best.url

        Instance = vlc.Instance()
        player = Instance.media_player_new()
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        player.set_media(Media)
        player.audio_set_volume(80)
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

#HERE
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


def get_emails():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    emails = INFO['emails']
    unread_status = {}
    message_count = 0
    for email in emails:
        unread_status[email] = 'read'
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(f'{email}.json'):
            creds = Credentials.from_authorized_user_file(f'{email}.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(f'{email}.json', 'w') as token:
                token.write(creds.to_json())

        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds = ['INBOX'],
                q='is:unread').execute()
        messages = results.get('messages', [])
        
        # Get number of messages
        if not messages:
            # No messages
            print(f'{email} has no new emails')
        else:
            # Tell user number of emails
            unread_status[email] = 'unread'
            message_count += len(messages)
            # Has unread messages
            if len(messages) == 1:
                print(f'{email} has 1 new email')
            else:
                print(f'{email} has {len(messages)} new emails')
    
    if message_count == 0:
        engine.say('You have no new emails!')
        engine.runAndWait()
    elif message_count == 1:
        engine.say(f'You have {message_count} total new email')
        engine.runAndWait()
    else:
        engine.say(f'You have {message_count} total new emails')
        engine.runAndWait()

    for email in emails:
        creds = Credentials.from_authorized_user_file(f'{email}.json', SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds = ['INBOX'],
                q='is:unread').execute()
        messages = results.get('messages', [])
        
        if unread_status[email] == 'unread':
            engine.say(f'Getting emails from {email}')
            engine.runAndWait()
            
        # Get emails
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


def get_calendar_events(command):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def authenticate_calendar():
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('calendar.json'):
            creds = Credentials.from_authorized_user_file('calendar.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('calendar.json', 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)
        return service

    def get_events(day, service):
        # Call the Calendar API
        # Get start of day and end of day dates
        date = day
        
        if date != datetime.date.today():
            date = datetime.datetime.combine(day, datetime.datetime.min.time())
        else:
            date = datetime.datetime.today()
            
        end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
        print(date)
        print(end_date)
        utc = pytz.UTC
        date = date.astimezone(utc)
        end_date = end_date.astimezone(utc)
        
        events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),
                                                timeMax = end_date.isoformat(), singleEvents=True,
                                                orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            
        print("DONE")

    def get_date(command):
        today = datetime.date.today()

        if command.count('today') > 0:
            return datetime.datetime.today()
        elif command.count('tomorrow') > 0:
            tomorrow = datetime.date.today() + datetime.timedelta(1)
            return tomorrow
        
        day = -1
        day_of_week = -1
        month = -1
        year = today.year
        day_of_week = -1
        
        for word in command.split():
            if word in MONTHS:
                month = MONTHS.index(word) + 1
            elif word in DAYS_OF_WEEK:
                day_of_week = DAYS_OF_WEEK.index(word)
            elif word.isdigit():
                day = int(word)
            else:
                for ext in DAY_EXTENSIONS:
                    found = word.find(ext)
                    if (found > 0):
                        try:
                            day = int(word[:found])
                        except:
                            pass
                        
        if (month < today.month and month != -1) or (day < today.day and day != -1):
            year = year + 1
            
        if day < today.day and month == -1 and day != -1:
            month = today.month + 1
            if month > 12:
                month = month % 12
                year = year + 1
            
        if month == -1 and day_of_week == -1:
            month = today.month
            
        if month == -1 and day == -1 and day_of_week != -1:
            current_day_of_week = today.weekday()
            diff = day_of_week - current_day_of_week
            
            if diff < 0:
                diff += 7
                    
            if command.count('next') > 0:
                diff += 7
                
            return today + datetime.timedelta(diff)

        return datetime.date(month=month, day=day, year=year)

    service = authenticate_calendar()
    try:
        date = get_date(command)
        get_events(date, service)
    except:
        print("invalid date")


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
            get_emails()
        elif 'calendar' in command or 'events' in command or 'schedule' in command:
            get_calendar_events(command)
        else:
            out = False
            for word in command.split():
                if word in MONTHS or word in DAYS_OF_WEEK:
                    get_calendar_events(command)
                    break
                else:
                    for ext in DAY_EXTENSIONS:
                        found = word.find(ext)
                        if found > 0:
                            try:
                                int(word[:found])
                                
                                get_calendar_events(command)
                                out = True
                                break
                            except:
                                pass
                    if out:
                        break
                        
            

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