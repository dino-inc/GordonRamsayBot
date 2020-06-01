import discord
from discord.ext import commands
import re
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class Modlog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Multiple sessionmakers between cogs for multiple points of access? What could go wrong!
        engine = create_engine('sqlite:///database.db')
        self.Session = sessionmaker(bind=engine)

async def log_deleted_meme(message):
    await modlog.send(embed=await mod_log_format("Terrible Meme Deleted",
                                                 f'Posted by {message.author}({message.author.id})'
                                                 f' at {message.created_at}.',
                                                 0xFF0000,
                                                 datetime.datetime.now()))


def setup(bot):
    bot.add_cog(Modlog(bot))
