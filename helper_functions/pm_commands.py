import sys
import os
import time

from helper_functions import senders
#from helper_functions import logging
from settings import bot_settings


def format_list(list):
    return ", ".join(list)

async def parse_command(ws, message, sender):

    # dictionary of possible commands and descriptions
    list_commands = {
        "help": "List all usable commands",
        "quit": "Exit program",
        "listteams": "List name of all available teams",
        "changeteam": "Change active team, example usage '$changeteam mane_team'",
        "sendcommand": "Manually send a command to PS, use $/ instead of |, e.g. '$sendcommand $//pm yoda2798, yoda is bad'",
        "restart": "Restart program, with updated code; may need extra code finishing up before restarting",
        "endtrial": "Stop logging the results of each battle",
        "autosearch": "Change setting for bot to automatically search for a new battle, e.g. '$autosearch true'"
    }

    # quit
    if (message == "$quit" or message == "$quirt"):
        await senders.send_pm(ws, "Exiting program", sender)
        print("Received quit message from {}, now exiting program".format(sender))
        time.sleep(1)  # wait 1 second so message sends before exiting
        sys.exit()
    # help
    elif (message[:5] == "$help"):
        if (len(message) == 5):
            await senders.send_pm(ws, "List of commands: {}".format(format_list(list(list_commands.keys()))), sender)
        elif(message[6:] in list_commands.keys()):
            help_cmd = message[6:]
            await senders.send_pm(ws, "{}: {}".format(help_cmd, list_commands[help_cmd]), sender)
        else:
            await senders.send_pm(ws, "Error: Invalid help command", sender)
    # list teams
    elif (message == "$listteams"):
        team_names = list(bot_settings.all_bot_teams.keys())
        await senders.send_pm(ws, "Available teams: {}".format(format_list(team_names)), sender)
    # change team
    elif (message[:11] == "$changeteam"):
        if (len(message) < 13 or message[12:] not in bot_settings.all_bot_teams.keys() ):
            await senders.send_pm(ws, "Error: Invalid team, use $listteams for available teams", sender)
        else:
            target_team = message[12:]
            bot_settings.active_bot_team = bot_settings.all_bot_teams[target_team]
            await senders.send_pm(ws, "Active team has been successfully changed", sender)
            print("Now using team {} for accepting challenges, as commanded by {}".format(target_team, sender))
    # send command
    elif (message[:12] == "$sendcommand" or message.split()[0] == "$sndcmd"):
        if (len(message) < 14):
            await senders.send_pm(ws, "Error: Invalid command, use $sendcommand for assistance", sender)
        else:
            send_cmd = message[13:].replace("$/","|")
            print("Sending following manual command to PS from user {}: {}".format(sender, send_cmd))
            await senders.send_command(ws, send_cmd)
            await senders.send_pm(ws, "Command sent", sender)
    # restart
    elif (message == "$restart"):
        await senders.send_pm(ws, "Restarting program", sender)
        print("Received restart message from {}, now restarting program".format(sender))
        time.sleep(1)  # wait 1 second so message sends before exiting and have time to see in command prompt
        #os.system("python main.py")
        #os.execl(sys.executable, 'python', __file__)
        os.execlp('python', 'python', 'main.py')
    # end trial
    elif (message == "$endtrial"):
        await senders.send_pm(ws, "Ending trial now...", sender)
        #logging.end_trial()
        await senders.send_pm(ws, "Trial ended!", sender)
    # autosearch setting
    elif (message.split()[0] in ["$autosearch", "$autosrch"]):
        if ( message.split()[1].lower() in ["true", "t", "on", "go"] ):
            already_searching = bot_settings.autosearch
            if (not already_searching): # start searching for game
                bot_settings.autosearch = True
                await senders.send_pm(ws, "Bot autosearch setting succesfully turned on", sender)
                await senders.search_for_battle(ws)
            else:
                await senders.send_pm(ws, "Bot autosearch setting already turned on", sender)
            print("Bot autosearch setting switched on by {}".format(sender))
        elif( message.split()[1].lower() in ["false", "f", "off", "stop"] ):
            bot_settings.autosearch = False
            await senders.send_pm(ws, "Bot autosearch setting succesfully turned off", sender)
            print("Bot autosearch setting switched off by {}".format(sender))
        else:
            await senders.send_pm(ws, "Error: Invalid command, use '$autosearch true' or '$autosearch false'", sender)
    # invalid command
    else:
        await senders.send_pm(ws, "Error: Invalid command, use $help for assistance", sender)
