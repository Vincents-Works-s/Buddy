from __future__ import print_function

import speech_recognition as sr
import pyttsx3
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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

import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

#------------------------------------------------------------------------------------

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

# Get date information
dt = datetime.datetime.now()
hour = dt.time().hour
minute = dt.time().minute
date = dt.date()
clock_time = dt.strftime("%I:%M %p")

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_EXTENSIONS = ['rd', 'th', 'st', 'nd']



lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.model')


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


def automated_greeting():
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




def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

print("GO! Running!")

while True:
    print("Type something!")
    message = input()
    ints = predict_class(message)
    print(ints)
    intent = ints[0]['intent']
    res = get_response(ints, intents)
    if intent == "automated greeting":
        automated_greeting()
    elif intent == "alarm clock":
        alarm_clock(19, 0)
    elif intent == "play song":
        play_song(song=message.partition('play ')[2])
    elif intent == "play my spotify playlist":
        play_my_spotify_playlist("2x02jcUK9zbZg7r72Y0LTK")
    elif intent == "get emails":
        get_emails()
    elif intent == "get calendar events":
        get_calendar_events(message)
    else:
        print(res)