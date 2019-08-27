#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
import pickle
import os.path
import iso8601
import pytz
from pytz import timezone
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import argparse
import random

from inky import InkyWHAT

from PIL import Image, ImageFont, ImageDraw
from font_amatic_sc import AmaticSC, AmaticSCBold
from font_hanken_grotesk import HankenGroteskSemiBold
from font_font_awesome import FontAwesome5FreeSolid, FontAwesome5Brands, FontAwesome5Free

def get_cal():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    active_events=[]
    next_events=[]
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        startobj = iso8601.parse_date(start).replace(tzinfo=timezone('America/Vancouver'))
        endobj = iso8601.parse_date(end).replace(tzinfo=timezone('America/Vancouver'))
        now = datetime.datetime.now()
        now = now.replace(tzinfo=timezone('America/Vancouver'))
        start = startobj.strftime('%s')
        end = endobj.strftime('%s')
        now = now.strftime('%s')
        if (now > start) and (now < end ) :
            active_events.append(event)
        else:
            next_events.append(event)
    active_ev = []
    for x in active_events:
        active_ev.append({'summary': x['summary'], 'start': x['start'], 'end': x['end']})
    if len(active_ev) < 1:
        active_ev.append({'start': '', 'end': '', 'summary': "Not In a Meeting"})
    active_ev.append({'summary': next_events[0]['summary'], 'start': next_events[0]['start'], 'end': next_events[0]['end']})
    return active_ev

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

print("""Inky wHAT: summarys

Display summarys on Inky wHAT.
""")

# Command line arguments to set display type and colour, and enter your name

colour = 'black'

# This function will take a summary as a string, a width to fit
# it into, and a font (one that's been loaded) and then reflow
# that summary with newlines to fit into the space required.


def reflow_summary(summary, width, font):
    words = summary.split(" ")
    reflowed = '"'
    line_length = 0
    max_lines = 3
    lines = 0
    truncate = False
    for i in range(len(words)):
        word = words[i] + " "
        word_length = font.getsize(word)[0]
        line_length += word_length
        if lines < 2:
            if line_length < width - icon_size - 30:
                reflowed += word
            else:
                line_length = word_length
                reflowed = reflowed[:-1] + "\n  " + word
                lines = lines + 1
        else:
            truncate = True
    if truncate:
        reflowed = reflowed.rstrip() + '..."'
    else:
        reflowed = reflowed.rstrip() + '"'
    return reflowed


# Set up the correct display and scaling factors
inky_display = InkyWHAT(colour)
inky_display.set_border(inky_display.WHITE)
# inky_display.set_rotation(180)

w = inky_display.WIDTH
h = inky_display.HEIGHT

# Create a new canvas to draw on

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the fonts

font_size = 26
time_size = 18
icon_size = 60

author_font = ImageFont.truetype(HankenGroteskSemiBold, time_size)
summary_font = ImageFont.truetype(HankenGroteskSemiBold, font_size)
icon_font = ImageFont.truetype(FontAwesome5Brands, icon_size)
icon_font2 = ImageFont.truetype(FontAwesome5FreeSolid, icon_size)

header_width = w
header_height = 80

# The amount of padding around the summary. Note that
# a value of 30 means 15 pixels padding left and 15
# pixels padding right.
#
# Also define the max width and height for the summary.

padding = 10
max_width = w - padding
max_height = h - padding - author_font.getsize("ABCD ")[1] - header_height

print(author_font.getsize("ABCD "))
below_max_length = False

# Only pick a summary that will fit in our defined area
# once rendered in the font and size defined.
events = get_cal()


if events[0]['summary'] != "Not In a Meeting" and 'dateTime' in events[0]['start'] and 'dateTime' in events[0]['end']:
    busy = True
    starttime = iso8601.parse_date(str(events[0]['start']['dateTime'])).replace(tzinfo=timezone('America/Vancouver'))
    starttime = starttime.strftime('%H:%M')
    endtime = iso8601.parse_date(str(events[0]['end']['dateTime'])).replace(tzinfo=timezone('America/Vancouver'))           # Pick a random person from our list
    endtime = endtime.strftime('%H:%M')
    message = events[0]['summary']
elif events[0]['summary'] == "Not In a Meeting":
    busy = False
    starttime = ''
    endtime = ''
    message = events[0]['summary']
else:
    busy = False
    events.pop(0)
    starttime = ''
    endtime = ''
    message = "Not In a Meeting"
summary = str(message)
next_start = iso8601.parse_date(str(events[1]['start']['dateTime'])).replace(tzinfo=timezone('America/Vancouver'))
next_start = next_start.strftime('%b %d  %H:%M')
reflowed = reflow_summary(summary, max_width, summary_font)
p_w, p_h = summary_font.getsize(reflowed)  # Width and height of summary
p_h = p_h * (reflowed.count("\n") + 1)   # Multiply through by number of lines

# x- and y-coordinates for the top left of the summary


summary_x = (w - max_width) / 2
summary_y = header_height + 10

# x- and y-coordinates for the top left of the author

author_x = summary_x
author_y = summary_y + p_h + 25

author = "Start Time: " + starttime + "  End Time: " + endtime
next_meeting = next_start
# Draw red rectangles top and bottom to frame summary
refresh_screen = False
state = author + next_meeting + summary
if os.path.exists('state.pickle'):
    with open('state.pickle', 'rb') as diskstate:
            if state == pickle.load(diskstate):
                refresh_screen = False
            else:
                with open('state.pickle', 'wb') as diskstate:
                    pickle.dump(state, diskstate)
                refresh_screen = True
else:
    with open('state.pickle', 'wb') as diskstate:
            pickle.dump(state, diskstate)
    refresh_screen = True
    


if refresh_screen == True:
    draw.rectangle((padding / 4, padding / 4, w - (padding / 4), header_height - (padding /4 )), fill=inky_display.BLACK, outline=inky_display.BLACK)
    draw.rectangle((padding / 4, author_y + author_font.getsize("ABCD ")[1] + (padding / 4) + (icon_size / 4), w - (padding / 4), h - (padding / 4)), fill=inky_display.BLACK, outline=inky_display.BLACK)


    # Write our summary and author to the canvas
    draw.text((10, 10), u"\uf2d7", fill=inky_display.WHITE, font=icon_font, align="left")
    draw.multiline_text((200, 10), "Liam's Office\nEtsy Inc", fill=inky_display.WHITE, font=summary_font, align="right")
    #draw.multiline_text((200, 10), "Etsy Inc", fill=inky_display.WHITE, font=summary_font, align="right")
    if busy:
        draw.text((max_width - icon_size - 10, summary_y), u"\uf056", fill=inky_display.BLACK, font=icon_font2, align="right")
        draw.multiline_text((summary_x, summary_y), "IN MEETING:\n" + reflowed, fill=inky_display.BLACK, font=summary_font, align="left")
        draw.multiline_text((author_x, author_y), author, fill=inky_display.BLACK, font=author_font, align="left")
    else:
        draw.text((max_width - icon_size - 10, summary_y), u"\uf52b", fill=inky_display.BLACK, font=icon_font2, align="right")
        draw.multiline_text((summary_x, summary_y), "OUT of MEETING:\n" + "Free", fill=inky_display.BLACK, font=summary_font, align="left")           
    draw.multiline_text(((padding / 4)+2, author_y + author_font.getsize("ABCD ")[1] + (padding / 4) + (icon_size / 3 )), "NEXT Meeting", fill=inky_display.WHITE, font=author_font, align="left")
    draw.multiline_text(((padding / 4)+2, author_y + author_font.getsize("ABCD ")[1] + (padding / 4) + (icon_size / 1.5 )), next_meeting, fill=inky_display.WHITE, font=author_font, align="left")

    #print(reflowed + "\n" + starttime + "\n" + endtime + "\n")

    # Display the completed canvas on Inky wHAT

    inky_display.set_image(img)
    inky_display.show()
