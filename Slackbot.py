from this import d
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import gspread

#steps to run:
    #Start ngrok (ngrok http 5000)
    #run program
    #Copy forwarding URL/slack/events to 'Event Subscription' on Slack API (Make sure to save changes)
    #launch slack

#Open file which connects to googlesheets API
sa = gspread.service_account(filename="%APPDATA%\gspread\service_account.json")
sh = sa.open("Test data")
wks = sh.worksheet("Sheet1")

#load .env file 
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#start web server with flask
app = Flask(__name__)

#Use slack event adapter to verify requests with signing secret
slack_event_adapter = SlackEventAdapter(
   os.environ.get('SIGNING_SECRET'),'/slack/events', app)

#Uses slack token to access slack API
client = slack.WebClient(token=os.environ.get('SLACK_TOKEN'))
BOT_ID = client.api_call("auth.test")['user_id']

@slack_event_adapter.on('message') #When message is sent
def message(payLoad): #assign payLoad to contain info from message
    event = payLoad.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if (BOT_ID != user_id) and ("help" in text.lower()): #If users string contains 'help'
        client.chat_postMessage(channel=channel_id, text="No!")
    if (BOT_ID != user_id) and ("google" in text.lower()): #If users string contains 'google'
        dataTest = wks.get_all_values() #create variable and assign it the list of lists from sheets
        dString = "Data from spreadsheet:\n" #initialize a string
        for x in dataTest: #iterate through that string
            for i in x:
                dString += i #add each variable in the list of lists as a string
                dString += " " # add a space between each variable
            dString += "\n" #add a new line for each list
        client.chat_postMessage(channel=channel_id,text=dString) #write the string into slack


if __name__ == "__main__":
    app.run(debug=True)

