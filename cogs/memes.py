import discord
from discord.ext import commands
import re
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import cogs.modlog as modlog
import cogs.config as config

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Multiple sessionmakers between cogs for multiple points of access? What could go wrong!
        engine = create_engine('sqlite:///database.db')
        self.Session = sessionmaker(bind=engine)


    @commands.Cog.listener()
    async def on_message(self, message):
        session = self.Session()
        serverdb = session.query(Server).filter_by(id=message.guild.id).first()
        # Check the channel for #memes
        if message.channel.id == serverdb.memes_id:
            # Hunt for the URL
            check_text = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                    message.content)
            # Delete message if the message is more than just a URL
            if message.content != check_text or message.content != "":
                #TODO - add logging
                #await log_deleted_meme(message)
                await message.delete()
            # Add emojis if all checks pass
            else:
                await message.add_reaction(config.get_emoji(message.ctx, upvote, session))
                await message.add_reaction(config.get_emoji(message.ctx, downvote, session))
        session.close()



def setup(bot):
    bot.add_cog(Memes(bot))
