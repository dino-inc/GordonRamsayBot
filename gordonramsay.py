import discord
from discord.ext import commands
import aiohttp
import re
import sys
import traceback
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String



# SQL Alchemy config
engine = create_engine('sqlite:///database.db', echo=True)
Base = declarative_base()


class Global(Base):
    __tablename__ = 'global'

    owner_id = Column(Integer, primary_key=True)
    upvote_emoji = Column(String)
    upvote_emoji_id = Column(Integer)
    downvote_emoji = Column(String)
    downvote_emoji_id = Column(Integer)

    def __repr__(self):
        return "Global(owner_id='%s', upvote_emoji='%s', upvote_emoji_id='%s', downvote_emoji='%s'," \
               " downvote_emoji_id='%s')>" % (
                self.owner_id, self.upvote_emoji, self.upvote_emoji_id, self.downvote_emoji, self.downvote_emoji_id)


class Server(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    shitposting_id = Column(Integer)
    memes_id = Column(Integer)
    worst_of_id = Column(Integer)
    best_of_id = Column(Integer)
    mod_log_id = Column(Integer)
    stars = Column(Integer)
    downstars = Column(Integer)
    upvotes = Column(Integer)
    downvotes = Column(Integer)

    def __repr__(self):
        return "Server(<id='%s', shitposting_id='%s', memes_id='%s', worst_of_id='%s', best_of_id='%s'," \
               " mod_log_id='%s', stars='%s', downstars='%s', upvotes='%s', downvotes='%s')>" % (
                self.id, self.shitposting_id, self.memes_id, self.worst_of_id, self.best_of_id, self.mod_log_id,
                self.stars, self.downstars, self.upvotes, self.downvotes)


Base.metadata.create_all(engine)

# Instantiate the bot object
bot = commands.Bot(command_prefix=';')

# Display this message upon startup
@bot.event
async def on_ready():
    print(f"Gordon Ramsay is online on {bot.user.name}, id {bot.user.id}.")

# Load startup cogs
initial_extensions=['cogs.config']
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