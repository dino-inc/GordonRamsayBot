import discord
from discord.ext import commands
import re
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine




class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Multiple sessionmakers between cogs for multiple points of access? What could go wrong!
        engine = create_engine('sqlite:///database.db')
        self.Session = sessionmaker(bind=engine)


    @commands.Cog.listener()
    async def on_message(self, message):
        session = new
        # Hunt for the URL
        check_text = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                message.content)
        # Delete message if the message is more than just a URL
        if message.content != check_text or message.content != "":
            await message.delete()
            print("Add in modlog stuff")
        else:
            await message.add_reaction(get_emoji(message.ctx, upvote, session))

async def get_id_val(ctx, val_name, tb_name, ctx, session):
    tb_object = session.query(tb_name).filter_by(id=ctx.guild.id).first()
    db_value = getattr(tb_object, f"{val_name}")
    session.close()
    return discord.utils.get(ctx.guild.channels, id=db_value)

async def get_emoji(ctx, emoji_name, session):
    tb_object = session.query("Global").first()
    emoji_id = getattr(tb_object, f"{emoji_name}")
    session.close()
    return discord.utils.get(ctx.guild.emojis, id=emoji_id)

def setup(bot):
    bot.add_cog(Memes(bot))
