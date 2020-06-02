import discord
from discord.ext import commands
import re
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from cogs import modlog
from cogs import config
import datetime

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
                await modlog.log_deleted_meme(message, "Talking in the meme channel", message.content, session)
                await message.delete()

        session.close()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        member = reaction.member
        guild = member.guild
        channel = guild.get_channel(reaction.channel_id)
        message = channel.get_message(reaction.message_id)
        session = self.Session()
        serverdb = config.get_server_ob(message, session)

        # worst of
        if reaction.emoji.id == 379319474639208458:
            await xboard(reaction, serverdb.downstars, message, serverdb)
        if reaction.emoji.id == '⭐':
            await xboard(reaction, serverdb.stars, message, serverdb)
        session.close()

async def xboard(reaction, reactionthreshold, message, serverdb):
    # Check to make sure post is eligible for board at all
    if message.channel.id == serverdb.memes_id \
            or message.channel.id == serverdb.best_of_id \
            or message.channel.id != worst_of_id:
        await message.remove_reaction(reaction.emoji, member)
        return
    # Check for ancient post reaction
    if check_date(reaction.message, 7):
        return
    # Remove self upvotes
    if message.author == message.guild.get_member(member.id):
        await message.remove_reaction(reaction.emoji, member)
        return
    # Iterate through reactions, to find the right one
    reactionlisttarget = None
    for x in message.reactions:
        if x.emoji == reaction.emoji:
            reactionlisttarget = x
    # Check if required threshold is reached
    if reactionlisttarget >= reactionthreshold:
        if reaction.emoji == '⭐':
            # TODO: read below
            generate_board_embed(reaction, message, 0xFFD700,
                                 f'Best of by: {message.author.display_name}',
                                 'https://upload.wikimedia.org/wikipedia/commons/f/f3/Star_Emoji.png')
        if reaction.emoji.id == 379319474639208458:
            # TODO: send embed returned
            generate_board_embed(reaction, message, 0xFF000,
                                 f"Worst of by: {message.author.display_name}",
                                 'http://rottenrat.com/wp-content/uploads/2011/01/Marty-Rathbun-anti-sign.jpg')

def generate_board_embed(reaction, message, color, title, icon_url):
    em = discord.Embed(description=message.content + '\n\n[Jump to post](' + message.jump_url + ')',
                       color=color, timestamp=message.created_at)
    em.set_author(name=title, icon_url=icon_url, url=message.jump_url)
    return em


def check_date(message, days):
    message_age = datetime.datetime.now() - message.created_at
    if message_age.days > days:
        print(f"Ignored reaction from more than {days} days ago.")
        return True
    else:
        return False

async def addvotes(message, session):
    await message.add_reaction(await config.get_emoji(message, "upvote_emoji_id", session))
    await message.add_reaction(await config.get_emoji(message, "downvote_emoji_id", session))

def setup(bot):
    bot.add_cog(Memes(bot))
