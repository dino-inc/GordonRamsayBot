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
        message = await channel.fetch_message(reaction.message_id)
        session = self.Session()
        serverdb = config.get_server_ob(message, session)
        # worst of
        if reaction.emoji.id == 379319474639208458:
            worstofchannel = guild.get_channel(serverdb.worst_of_id)
            await xboard(reaction, serverdb.downstars, message, serverdb, worstofchannel)
        if reaction.emoji.name == '⭐':
            bestofchannel = guild.get_channel(serverdb.best_of_id)
            await xboard(reaction, serverdb.stars, message, serverdb, bestofchannel)
        session.close()

async def xboard(reaction, reactionthreshold, message, serverdb, pinchannel):
    # Check to make sure post is eligible for board at all
    if message.channel.id == serverdb.memes_id \
            or message.channel.id == serverdb.best_of_id \
            or message.channel.id == serverdb.worst_of_id:
        await message.remove_reaction(reaction.emoji, message.author)
        return
    # Check for ancient post reaction
    if check_date(message, 7):
        return
    # Remove self upvotes
    # if message.author == message.guild.get_member(reaction.member.id):
        #await message.remove_reaction(reaction.emoji, message.author)
        #return
    # Iterate through reactions, to find the right one
    reactionlisttarget = None
    for x in message.reactions:
        if x.emoji == reaction.emoji.name:
            reactionlisttarget = x
    # Check if required threshold is reached
    if reactionlisttarget.count >= reactionthreshold:
        if reaction.emoji.name == '⭐':
            # TODO: read below
            em = await generate_board_embed(reaction, message, 0xFFD700,
                                 f'Best of by: {message.author.display_name}',
                                 'https://upload.wikimedia.org/wikipedia/commons/f/f3/Star_Emoji.png')

        elif reaction.emoji.id == 379319474639208458:
            # TODO: send embed returned
            em = await generate_board_embed(reaction, message, 0xFF000,
                                 f"Worst of by: {message.author.display_name}",
                                 'http://rottenrat.com/wp-content/uploads/2011/01/Marty-Rathbun-anti-sign.jpg')
        else:
            return
        await pinchannel.send(embed = em)
async def generate_board_embed(reaction, message, color, title, icon_url):
    em = discord.Embed(description= message.content,
                       color=color, timestamp=message.created_at)
    em.set_author(name=title, icon_url=icon_url, url=message.jump_url)
    em = await handle_image_embed(em, message)
    em.add_field(name="\u200b", value='[Jump to post](' + message.jump_url + ')')
    return em

async def handle_image_embed(em, message):
    if len(message.embeds) > 0:
        em.set_image(url=message.embeds[0].url)
        return em
    if len(message.attachments) > 0:
        attach_list = ""
        for atta in message.attachments:
            attach_list += f"{atta.url}\n"
        em.add_field(name="\u200b", value=f"{attach_list}", inline=True)
        em.set_image(url=message.attachments[0].url)
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
