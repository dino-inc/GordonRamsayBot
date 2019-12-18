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
        for filename in os.listdir('./cog'):
            filename = os.path.splitext(filename)[0]
            print(f'Loading cogs.{filename}')
            try:
                bot.load_extension(f'cogs.{filename}')
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