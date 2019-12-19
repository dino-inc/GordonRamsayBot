import discord
from discord.ext import commands
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        engine = create_engine('sqlite:///database.db')
        self.Session = sessionmaker(bind=engine)



def get_server_val(val_name, )
    session.query(Server).filter_by(id=ctx.guild.id).first().id

def setup(bot):
    bot.add_cog(Memes(bot))
