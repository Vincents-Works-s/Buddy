from __future__ import print_function
import pyttsx3
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time
from google.oauth2.credentials import Credentials
import speech_recognition as sr
from fuzzywuzzy import fuzz

# check if user said email name
# if not, then give number of emails for all emails
# so: 1, if user asks for an email, show unread count and emails
#     2, if asking for any new mail, show number of unread for all emails
#USE THREADING - give number of accounts with unread messages

# Set up mic and tts voice
recognizer = sr.Recognizer()
microphone = sr.Microphone()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

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

def get_emails():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    EMAILS = ['22vincentruan@gmail.com',
              'vincent.ruan@sjsu.edu']
    print(EMAILS)
    unread = False
    message_count = 0
    # Print emails and email count
    for email in EMAILS:
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

        if not messages:
            print(f'{email} has no new emails')
            # engine.say(f'{email} has no new emails')
            # engine.runAndWait()
        else:
            # Tell user number of emails, show if requested
            message_count += len(messages)
            # Has unread messages
            unread = True
            if len(messages) == 1:
                print(f'{email} has 1 new email')
                # engine.say(f'{email} has one new email')
                # engine.runAndWait()
            else:
                print(f'{email} has {len(messages)} new emails')
                # engine.say(f'{email} has {message_count} new emails')
                # engine.runAndWait()

    if not unread:
        engine.say('No new emails!')
        engine.runAndWait()
        return

    if message_count == 1:
        engine.say(f'You have {message_count} total new email.')
        engine.runAndWait()
    else:
        engine.say(f'You have {message_count} total new emails.')
        engine.runAndWait()

    engine.say('Which email would you like to view?')
    engine.runAndWait()

    while True:
        command = take_command()
        print(command)
        if command is False:
            continue
        high = 0
        email = ''
        for i in EMAILS:
            fuzz_ratio = fuzz.WRatio(command, i)
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
            return
        break

    print(f'{email}:')
    engine.say(f'Getting emails from {email}...')
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

get_emails()