# dependencies
import os
import time
import re
from slackclient import SlackClient

# oAuth
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# gallagherbot's user ID in Slack: the value is assigned after the bot starts up
gallagherbot_id = None


# constants
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
        response = "as you were"

    if command.startswith("rockstars"):
        response = "Name one rock star in Britain apart from a member of Oasis. Name one!"

    if command.startswith("bank holidays"):
        response = "We don’t observe bank holidays in this band. It’s all one big bank holiday, one big fucking day off."

    if command.startswith("chris martin"):
        response = "I don`t hate Chris Martin. I don`t know him, know what I mean? I just thinks he`s a bit giddy. He ought to calm down, he isn`t gonna save the world"

    if command.startswith("glastonbury"):
        response = "I f***ing hate Glastonbury, mate. I’m only here for the money"

    if command.startswith("beatles"):
        response = "We will be as big as the Beatles, if not bigger"

    if command.startswith("a$ap rocky"):
        response = "My kids also like that bloke, WhatsApp Ricky. You know, the American geezer, stylish, funny, gold teeth"

    if command.startswith("god"):
        response = "I mean, the devil's got all the good gear. What's God got? The Inspiral Carpets and nuns. F*** that"

    if command.startswith("knebworth"):
        response = "I did the whole Knebworth set in the shower earlier. It was f***ing great"

    if command.startswith("beady eye"):
        response = "Everyone'll be calling their kids Beady Eye by the end of the year"

    if command.startswith("charlotte church"):
        response = "It's Charlotte Church for me, man. She could be the next Liam."
   
    if command.startswith("the sun"):
        response = "The Sun? There's a load of c**ts at that newspaper"

    if command.startswith("hair"):
        response = "There’s no place for baldness in rock n roll"

    if command.startswith("fog"):
        response = "Turn that fucking shit fog machine off"

    if command.startswith("liam"):
        response = "They think I'm a big-mouthed c**t from Manchester, and they’d be correct"

    if command.startswith("football"):
        response = "I’m moving back to Manchester if City win the league. I’m going to buy a house next to Mani out of Stone Roses and be a real noisy neighbour – hurl abuse at him over the fence"

    if command.startswith("gary neville"):
        response = "If the world was full of f**king Gary Nevilles, it would be bobbins. He looks like an estate agent"

    if command.startswith("bono"):
        response = "You see pictures of Bono running around LA with his little white legs and a bottle of Volvic"

    if command.startswith("dancing"):
        response = "I refuse to dance. And I can't dance anyway. I'm not in a band for that"

    if command.startswith("george harrison"):
        response = "I still love George Harrison as a songwriter in the Beatles, but as a person I think he’s a f**king nipple"

    if command.startswith("gardens"):
        response = "I much prefer it be f**king paved. The minute I get some money in the bank there’ll be f**king concrete going over it"

    if command.startswith("swimming"):
        response = "I can't swim. I can have a bath and that. I'm all right in a hot tub. But put me out in the ocean and I'm gone"

    if command.startswith("blur"):
        response = "Being a lad is what I'm about. I can tell you who isn't a lad - anyone from Blur"

    if command.startswith("cardigans"):
        response = "I have got a bit of an issue with cardigans. They’re shit aren’t they?"

    if command.startswith("kaiser chiefs"):
        response = "Nothing worse than a shit Blur"

    if command.startswith("elvis"):
        response = "There`s Elvis and me. I couldn`t say which of the two is best"

    if command.startswith("u2"):
        response = "I have never seen a U2 fan. I have never seen anyone with a U2 shirt or been around someone's house that has a f***ing U2 record. Where do their fans f***ing come from?"


    # this sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response,
        icon_url = 'https://i.imgur.com/P3rfqP2.jpg',
        username = 'Liam Gallagher',
        as_user = False
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


