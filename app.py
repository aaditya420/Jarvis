import os
import TimeTable
import pandas as pd
import random as rd
import pyautogui as pg
import ctypes
import time
from googlesearch import search
import kg_api

from flask import Flask, render_template, request
from requests_html import HTMLSession
from twilio.rest import Client

from config import *

pg.PAUSE = 0.1

app = Flask(__name__)

# Helper function to send WhatsApp messages
def send_message(to, body, media=None):
    # Initialize client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=body,
        from_=WHATSAPP_FROM_NUMBER,
        to=to,
        media_url=media
    )

# Helper function to get an emoji's description
def get_emojipedia_description(character):
    # Get the Emojipedia page for this emoji
    session = HTMLSession()
    response = session.get('https://emojipedia.org/' + character)

    # If we didn't find an emoji, say so
    if not response.ok:
        return "Hmm - I couldn't find that emoji. Try sending me a single emoji ☝️"

    # Extract the title and description using Requests-HTML and format it a bit
    title = response.html.find('h1', first=True).text
    description = response.html.find('.description', first=True)
    description = '\n\n'.join(description.text.splitlines()[:-1])

    # And template it
    return render_template(
        'response.txt',
        title=title,
        description=description,
        url=response.url
    )

@app.route('/', methods=['GET', 'POST'])
def receive_message():
    # Get the querie
    querie = request.values.get('Body')
    print(querie)

    reply = parse_msg(querie)
    print(reply)

    send_message(to=request.values['From'], body=reply)

    return ('', 204)


def Main():

    try:
        pd.read_csv("TimeTable.csv")
        # TimeTable.render_mpl_table(df, header_columns=1, col_width=7).get_figure().savefig("TimeTable.png", dpi=200)
    except:
        TimeTable.get_time_table()


def hibernate():
    pg.press("win")
    pg.press("tab", 2, 0.1)
    pg.press("down", 3, 0.1)
    pg.press("space")
    pg.press("down")
    pg.press("space")


def parse_msg(ql):

    greetings = [
        "Hi there! How's it going? I am JARVIS, How may I help you?",
        "Hola Amigo! How can I be of help?",
        "Heya! What's Up? How can I help ya?",
        "Good Day mate! How can I be of any help to ya?!"
    ]

    see_offs = [
        "Have a good day!",
        "Pleasure helping you!",
        "Have a good one mate!",
        "Adios b*tch!",
        "Sayonara!"
    ]

    errors = [
        "I am sorry I quiet did not get that, please rephrase?",
        "Pardon me?",
        "I did not understand that, sorry!",
        "I am sorry can you please be more specific?",
        "B*tch I don't do that sh*t no more!",
        "Are you okay? Coz this is something I cannot do!",
        "Please say something sensible you moron!",
        "Oh God!  Please make some sense!",
        "I cannot take this sh*t no more, please say something sensible!"
    ]

    ql = ql.lower()

    f = 0

    resp = ""

    if ("hi" in ql) or ("hello" in ql) or ("good morning" in ql) or ("hola" in ql) or ("hey" in ql):
        resp = rd.choice(greetings) + " "
        f = 1
    
    if ("thank" in  ql) or ("bye" in ql):
        resp += rd.choice(see_offs)
        f = 1
    
    if (("lock" in ql) and ("pc" in ql)):
        resp += "You're PC has been locked! "
        ctypes.windll.user32.LockWorkStation()
        f = 1

    if ("hibernate" in ql) and ("pc" in ql):
        resp += "You're PC has been hibernated! " + rd.choice(see_offs)
        f = 1
        hibernate()
    
    if ("send" in ql) and ("time table" in ql):
        send_message(request.values['From'], "Here you go!", TT_URL)
        resp += "Happy to Help! "
        f = 1

    if ("send" in ql) and ("screen shot" in ql):
        pg.screenshot("AutoScreenShot.png")
        time.sleep(10)
        send_message(request.values['From'], "Here you go!", SS_URL)
        resp += "Hope that Helped! "
        f = 1
    
    if ("google" in ql):
        resp += "Here is what I found:\n\n"
        s = " ".join(ql.split()[ql.split().index("google")+1:])
        print(s)
        
        j = 1
        for i in kg_api.google_search(s):
            if "sorry! coudn't" in i.lower():
                break
            if len(resp) < 1000:
                if i[-2] == "-":
                    for k in search(i.split("*")[1], stop=1, tld="co.in"):
                        resp += "*" + str(j) + "*. " + i + " " + k + "\n\n"    
                        j += 1
                else:
                    resp += "*" + str(j) + "*. " + i + "\n\n"    
                    j += 1
        
        # for i in search(s, num=5, stop=10, tld="co.in"):
        #     resp += "*" + str(j) + ".* " + i + "\n\n"
        
        f = 1
    
    if ("update" in ql) and ("time table" in ql):
        TimeTable.get_time_table()
        resp += "Time Table successfully updated! "
        f = 1

    if ("next" in ql) and ("class" in ql):
        resp += TimeTable.fetch_next_room_number(pd.read_csv("TimeTable.csv")) + " "
    
    elif (("current" in ql) or ("now" in ql) or ("right" in ql)) and ("class" in ql):
        resp += TimeTable.fetch_next_room_number(pd.read_csv("TimeTable.csv"), False) + " "
    
    elif (len(ql) == 1) and (ord(ql) > 200):
        resp = get_emojipedia_description(ql)
    
    elif f == 0:
        resp += "Here is what I found:\n\n"
        # s = " ".join(ql.split()[ql.split().index("google")+1:])
        # print(s)
        
        j = 1
        for i in kg_api.google_search(ql):
            if "sorry! coudn't" in i.lower():
                break
            if len(resp) < 1000:
                if i[-2] == "-":
                    for k in search(i.split("*")[1], stop=1, tld="co.in"):
                        resp += "*" + str(j) + "*. " + i + " " + k + "\n\n"    
                        j += 1
                else:
                    resp += "*" + str(j) + "*. " + i + "\n\n"    
                    j += 1

        if "sorry! coudn't" in resp.lower():
            resp = rd.choice(errors)
    
    print(len(resp))

    return resp


if __name__ == "__main__":
    Main()
    app.run(debug=True)