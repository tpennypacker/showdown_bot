import sys
import time

from helper_functions import senders
from settings import bot_settings


def format_list(list):
    return ", ".join(list)

async def parse_command(ws, message, sender):

    # dictionary of possible commands and descriptions
    list_commands = {"help": "List all usable commands", "quit": "Exit program", "listteams": "List name of all available teams", "changeteam": "Change active team, example usage '$changeteam mane_team'"}

    # quit
    if (message == "$quit" or message == "$quirt"):
        await senders.send_pm(ws, "Exiting program", sender)
        print("Received quit message from {}, now exiting program".format(sender))
        time.sleep(1)  # wait 1 second so message sent
        sys.exit()
    # help
    elif (message[:5] == "$help"):
        if (len(message) == 5):
            #print("List of commands: {}".format(", ".join(list(list_commands.keys()))))
            await senders.send_pm(ws, "List of commands: {}".format(format_list(list(list_commands.keys()))), sender)
        elif(message[6:] in list_commands.keys()):
            help_cmd = message[6:]
            await senders.send_pm(ws, "{}: {}".format(help_cmd, list_commands[help_cmd]), sender)
            #print("{}: {}".format(help_cmd, list_commands[help_cmd]))
        else:
            await senders.send_pm(ws, "Error: Invalid help command", sender)
    # list teams
    elif (message == "$listteams"):
        team_names = list(bot_settings.all_bot_teams.keys())
        await senders.send_pm(ws, "Available teams: {}".format(format_list(team_names)), sender)
        #print("Received list_teams message from {}, listing available teams".format(sender))
    # change team
    elif (message[:11] == "$changeteam"):
        print(message[12:])
        if (len(message) < 13 or message[12:] not in bot_settings.all_bot_teams.keys()):
            await senders.send_pm(ws, "Error: Invalid team, use $listteams for available teams", sender)
            #print("Received invalid $change_team message from {}".format(sender))
        else:
            target_team = message[12:]
            bot_settings.active_bot_team = bot_settings.all_bot_teams[target_team]
            await senders.send_pm(ws, "Active team has been successfully changed", sender)
            #print(bot_settings.all_bot_teams[target_team])
            print("Now using team {} for accepting challenges, as commanded by {}".format(target_team, sender))
    # invalid command
    else:
        await senders.send_pm(ws, "Error: Invalid command, use $help for assistance", sender)
