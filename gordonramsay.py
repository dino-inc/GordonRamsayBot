import discord
import configparser
import aiohttp
import re
import sys
import traceback
import os

# Setting up the config if none is found
config = configparser.ConfigParser()
if not os.path.exists('config.ini'):
    print("No config file found, regenerating config.ini.")

    # Default values for the config
    botconfig['GLOBAL'] = {'owner_id': '141695444995670017',
                       'stars': '7',
                       'downstars': '5',
                       'upvotes': '27',
                       'downvotes': '6',
                       'upvote_emoji': ':upvote:335141910773628928',
                       'downvote_emoji': ':downvote:335141916989456384',
                       'upvote_emoji_id': '335141910773628928',
                       'downvote_emoji_id': '335141916989456384',
                       'use_test_guild': 'false'}
    botconfig['Meme Economy'] = {'guild_id': '231084230808043522',
                             'shitposting_id': '300377971234177024',
                             'memes_id': '313400507743862794',
                             'worst_of_id': '395695465955328000',
                             'best_of_id': '300792095688491009',
                             'mod_log_id': '318907499753242634'}
    botconfig['Test Server'] = {'guild_id': '277294377548775425',
                            'shitposting_id': '396748832932626433',
                            'memes_id': '396748843397414914',
                            'worst_of_id': '396748875362336779',
                            'best_of_id': '396748860174630912',
                            'mod_log_id': '538088043245207563'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
botconfig.read('config.ini')

# Instantiate the bot object
bot = commands.Bot(command_prefix=';')

# Display this message upon startup
@bot.event()
async def on_ready():
    print(f"Gordon Ramsay is online on {bot.user.name}, id{bot.user.id}.")

# Load startup cogs
if __name__ == '__main__':
    for extension in initial_extensions:
        print(f'Loading {extension}.')
        try:
            bot.load_extension(extension)
            print('Finished loading.')
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

# Process the commands from each message input
@bot.event
async def on_message(message):
    await bot.process_commands(message)

# Run the bot using the bot token
token = open("token.txt", 'r')
bot.run(token.read(), bot = True, reconnect=True)