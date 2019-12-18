import discord
from discord.ext import commands
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import exc
import asyncio

Base = declarative_base()
engine = create_engine('sqlite:///database.db')

class Global(Base):
    __tablename__ = 'global_vars'

    owner_id = Column(Integer, primary_key=True)
    upvote_emoji_id = Column(Integer)
    downvote_emoji_id = Column(Integer)

    def __repr__(self):
        return "Global:\nowner_id='%s'\nupvote_emoji_id='%s'\ndownvote_emoji_id='%s'" % (
                self.owner_id, self.upvote_emoji_id, self.downvote_emoji_id)


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
        return "Server:\nid='%s'\nshitposting_id='%s'\n memes_id='%s'\nworst_of_id='%s'\nbest_of_id='%s'\n" \
               "mod_log_id='%s'\nstars='%s'\ndownstars='%s'\nupvotes='%s'\ndownvotes='%s'" % (
                self.id, self.shitposting_id, self.memes_id, self.worst_of_id, self.best_of_id, self.mod_log_id,
                self.stars, self.downstars, self.upvotes, self.downvotes)


Base.metadata.create_all(engine)

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        engine = create_engine('sqlite:///database.db')
        self.Session = sessionmaker(bind=engine)

    # The config group of commands.
    @commands.group(name="config",
               invoke_without_command=True,
               help="The group of config commands.")
    @commands.is_owner()
    async def config(self, ctx):
        session = self.Session()
        server_object = Server(id=ctx.guild.id)
        global_object = Global(owner_id=ctx.author.id)
        try:
            session.add(server_object)
            session.add(global_object)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            await ctx.send(f"This server({session.query(Server).filter_by(id=ctx.guild.id).first().id})"
                           f" has already been created in the database.")
            session.close()
            return

        await ctx.send(f"Server {ctx.guild.name} added to the database.")

    @config.command()
    @commands.is_owner()
    async def set_server_var(self, ctx, var_name, var_value):
        session = self.Session()
        server_vars = get_server_ob(ctx, session)
        old_value = getattr(server_vars, f"{var_name}")
        setattr(server_vars, f"{var_name}", var_value)
        await ctx.send(f"Changed the value from {old_value} to {getattr(server_vars, f'{var_name}')}.")
        session.commit()
        session.close()

    @config.command()
    @commands.is_owner()
    async def set_global_var(self, ctx, var_name, var_value):
        session = self.Session()
        global_vars = session.query(Global).filter_by(owner_id=ctx.author.id).first()
        old_value = getattr(global_vars, f"{var_name}")
        setattr(global_vars, f"{var_name}", var_value)
        await ctx.send(f"Changed the value from {old_value} to {getattr(global_vars, f'{var_name}')}.")
        session.commit()
        session.close()

    @config.command()
    @commands.is_owner()
    async def channels(self, ctx):
        # channels
        channels = ['shitposting_id', 'memes_id', 'worst_of_id', 'best_of_id', 'mod_log_id',
                    # not channels
                    'stars', 'downstars', 'upvotes', 'downvotes']
        session = self.Session()
        server_vars = get_server_ob(ctx, session)
        await multi_user_input(ctx, self, session, server_vars, channels)
        verification_msg = ""
        for value_name in channels:
            id_attr = getattr(server_vars, f"{value_name}")
            verification_msg += f"{value_name}: `{id_attr}`\n"
        await ctx.send(verification_msg)
        session.commit()
        session.close()

    @config.command()
    @commands.is_owner()
    async def globals(self, ctx):
        globals = ['owner_id', 'upvote_emoji_id', 'downvote_emoji_id']
        session = self.Session()
        global_vars = session.query(Global).filter_by(owner_id=ctx.author.id).first()
        await multi_user_input(ctx, self, session, global_vars, globals)
        verification_msg = ""
        for var_name in globals:
            id_attr = getattr(global_vars, f"{var_name}_id")
            verification_msg += f"{var_name}: `{id_attr}`\n"
        await ctx.send(verification_msg)
        session.commit()
        session.close()

    @config.command()
    @commands.is_owner()
    async def print(self, ctx):
        session = self.Session()
        server_vars = get_server_ob(ctx, session)
        global_vars = session.query(Global).filter_by(owner_id=ctx.author.id).first()
        await ctx.send(str(global_vars) +'\n' + str(server_vars))

def get_server_ob(ctx, session):
    return session.query(Server).filter_by(id=ctx.guild.id).first()


async def multi_user_input(ctx, self, session, datatype_vars, item_array):
    # Ensures the responding user matches the one who started the command and is in the same channel
    def verify_user(message):
        if message.author == ctx.message.author and message.channel == ctx.message.channel:
            return True
        else:
            return False

    composite_msg = ""
    for item_name in item_array:
        composite_msg += f"What is the {item_name} value?"
        await ctx.send(composite_msg)
        try:
            choice = await self.bot.wait_for('message', check=verify_user, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send(f"No input found, exiting value config.")
            session.close()
            return
        setattr(datatype_vars, f"{item_name}", choice.content)
        composite_msg = f"Set {item_name}'s ID to `{choice.content}`\n"
    await ctx.send(composite_msg)



def setup(bot):
    bot.add_cog(Config(bot))
