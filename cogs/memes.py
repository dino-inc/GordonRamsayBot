import discord
from discord.ext import commands
import re
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from cogs import modlog
from cogs import config

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Multiple sessionmakers between cogs for multiple points of access? What could go wrong!
        engine = create_engine('sqlite:///database.db')
        self.Session = sessionmaker(bind=engine)


    @commands.Cog.listener()
    async def on_message(self, message):
        session = self.Session()
        serverdb = config.get_server_ob(message, session)
        # Check the channel for #memes
        if message.channel.id == serverdb.memes_id:
            # Hunt for the URL
            check_text = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                    message.content)
            # Check for normal text being posted
            if message.content == "" or check_text:
                await addvotes(message, session)
            # Delete if it is not found to be a URL or image embed
            else:
                #TODO - add logging
                await message.delete()

        session.close()

async def addvotes(message, session):
    await message.add_reaction(await config.get_emoji(message, "upvote_emoji_id", session))
    await message.add_reaction(await config.get_emoji(message, "downvote_emoji_id", session))

def setup(bot):
    bot.add_cog(Memes(bot))
