# before I began I $ pip install virtualenv and $ pip install slackclient


# importing dependancies from slackclient
import os
import time
import re
from slackclient import SlackClient

# instantiate the slack client using the bot oAuth token saved as a variable
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# gallagherbot's user ID in Slack: the value is assigned after the bot starts up
gallagherbot_id = None

# some constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "liam" # slack command that will prompt gallagherbot
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"




# -------- function 1 (listens for commands) -----------

def parse_bot_commands(slack_events):
    
    # parses a list of events coming from the Slack RTM API to find bot commands.
    # it only listens for 'message events' and filters out other events based on event properties
    # if a bot command is found, this function returns a tuple of command and channel.
    # if it is not found, then this function returns None, None.
    
    for event in slack_events:

    	# 'type' and 'subtype' are Object Types found in Slack's API. The commands we want to find, have no subtype.
        if event["type"] == "message" and not "subtype" in event:

        	# once we know the event contains a message, we call the 'parse_direct_mention' function to determine 
        	# whether the mention matches the @gallagherbot's user id we stored earlier
        	# if this matches up, we return the command text with the Slack channel id
            user_id, message = parse_direct_mention(event["text"])
            if user_id == gallagherbot_id:
                return message, event["channel"]
    return None, None


# -------- function 2 (listens for direct mentions) -------

def parse_direct_mention(message_text):
    
    # finds a direct mention in message_text i.e. @gallagherbot (but only if the mention is at the beginning of the message)
    # and returns the user ID which was mentioned (@gallagherbot's id) and the rest of the message
    # if there is no direct mention, it returns 'None, None'
    
    matches = re.search(MENTION_REGEX, message_text)

    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


# -------- function 3 (listens for a known command) -------

def handle_command(command, channel):
    
    # executes bot command if the command is known
    # if the command starts with a known command, it will have an appropriate response 
    # if it doesn't, a default response is used which we determine here 
    # the response is sent back to Slack by calling the chat.postMessage Web API method with the channel
    
    # default text response to help the user if the command is wrong 
    default_response = "Try *{}*, as you were".format(EXAMPLE_COMMAND)

    # finds and executes the given command, filling in response
    response = None

    # the commands
    if command.startswith(EXAMPLE_COMMAND):
        response = "hi i'm liam"

    # this sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )



# --------------------------------

if __name__ == "__main__":

	# connecting the Slack Client to Slack RTM (real time messenger) API, this calls the 'auth.test' web API method 
	# which checks the authentication & identity of the bot. If this passes we should see "gallagherbot, as you were" as output

    if slack_client.rtm_connect(with_team_state=False):
        print("gallagherbot, as you were")

        # reads gallagherbot's user ID by calling the Web API method `auth.test`. 
        # this should help the program recognise when gallaherbot has been mentioned in a message 

        gallagherbot_id = slack_client.api_call("auth.test")["user_id"]

        # each time the while loop runs the Slack Client recieves any events that have arrived from Slack's RTM API. 
        # before the loop ends, the program pauses for one second so as not to waste CPU time.
        # parse_bot_commands() listens for events relevant to gallagherbot for example specified commands

        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())

            # if a command is heard by parse, then 'command' will contain a value and the 
            # 'handle_command()' function will determine what to do with the command

            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
