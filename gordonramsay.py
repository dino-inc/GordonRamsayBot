import discord
from discord.ext import commands
import aiohttp
import re
import sys
import traceback
import os



# Instantiate the bot object
bot = commands.Bot(command_prefix=';')

# Display this message upon startup
@bot.event
async def on_ready():
    print(f"Gordon Ramsay is online on {bot.user.name}, id {bot.user.id}.")
    # Load startup cogs
    initial_extensions = ['cogs.config']
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