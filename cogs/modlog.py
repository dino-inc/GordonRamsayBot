import discord
from discord.ext import commands
import re
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from cogs import config
import datetime

class Modlog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Multiple sessionmakers between cogs for multiple points of access? What could go wrong!
        engine = create_engine('sqlite:///database.db')
        self.Session = sessionmaker(bind=engine)


async def log_deleted_meme(message, reason, content, session):
    serverdb = config.get_server_ob(message, session)
    modlog = discord.utils.get(message.guild.text_channels, id=serverdb.mod_log_id)
    await modlog.send(embed=discord.Embed(description=f'Posted by {message.author}({message.author.id})'
                                                      f' at {message.created_at}.\n Content: {content}',
                        colour=0xFF0000,
                        title=f"{reason}",
                        timestamp=datetime.datetime.now()))

def setup(bot):
    bot.add_cog(Modlog(bot))
