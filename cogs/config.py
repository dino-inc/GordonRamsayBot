import discord
from discord.ext import commands
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import exc


Base = declarative_base()
engine = create_engine('sqlite:///database.db')

class Global(Base):
    __tablename__ = 'global_vars'

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
        try:
            session.add(server_object)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            await ctx.send(f"This server({session.query(Server).filter_by(id=ctx.guild.id).first().id})"
                           f" has already been created in the database.")
            session.close()
            return

        await ctx.send(f"Server {ctx.guild.name} added to the database.")

    # Sets the number of upvotes for best_of.
    @config.command(name="upvotes",
                    help="Sets the number of upvotes required for best_of in the server",
                    brief="Sets upvotes for the memes channel.")
    @commands.is_owner()
    async def upvotes(self, ctx, upvote_count):
        session = self.Session()
        server_vars = get_server_ob(ctx, session)

        old_value = server_vars.upvotes
        server_vars.upvotes = upvote_count
        session.commit()
        print(f"{ctx.author.name} (ID:  {ctx.author.id}) changed upvotes for best_of from"
              f" {old_value} to {server_vars.upvotes}")
        await ctx.send(f"Changed the best_of upvote threshold from {old_value} to {server_vars.upvotes}")
        session.close()

    @config.command(name="downvotes",
                    help="Sets the number of downvotes required to delete a meme in the meme channel",
                    brief="Sets downvotes for the meme channel.")
    @commands.is_owner()
    async def downvotes(self, ctx, downvote_count):
        session = self.Session()
        server_vars = get_server_ob(ctx, session)

        old_value = server_vars.downvotes
        server_vars.downvotes = downvote_count
        session.commit()
        print(f"{ctx.author.name} (ID:  {ctx.author.id}) changed downvotes for deletion from"
              f" {old_value} to {server_vars.downvotes}")
        await ctx.send(f"Changed the deletion threshold from {old_value} to {server_vars.downvotes}")
        session.close()

    @config.command(name="stars",
                    help="Sets the number of stars required for best_of in the server",
                    brief="Sets stars for the server.")
    @commands.is_owner()
    async def stars(self, ctx, star_count):
        session = self.Session()
        server_vars = get_server_ob(ctx, session)

        old_value = server_vars.stars
        server_vars.stars = star_count
        session.commit()
        print(f"{ctx.author.name} (ID:  {ctx.author.id}) changed stars for best_of from"
              f" {old_value} to {server_vars.downstars}")
        await ctx.send(f"Changed the best_of star threshold from {old_value} to {server_vars.stars}")
        session.close()

    @config.command(name="downstars",
                    help="Sets the number of downstars required to send a post to worst_of in the server",
                    brief="Sets worst_of stars for the memes channel.")
    @commands.is_owner()
    async def downstars(self, ctx, downstar_count):
        session = self.Session()
        server_vars = get_server_ob(ctx, session)

        old_value = server_vars.downstars
        server_vars.downstars = downstar_count
        session.commit()
        print(f"{ctx.author.name} (ID:  {ctx.author.id}) changed downstars for worst_of from"
              f" {old_value} to {server_vars.downstars}")
        await ctx.send(f"Changed the worst_of star threshold from {old_value} to {server_vars.downstars}")
        session.close()

    @config.command()
    @commands.is_owner()
    async def channels(self, ctx):

        def check_inline(message):
            if message.author.id == ctx.author.id:
                return True
            else:
                return False

        channels = ['shitposting', 'memes', 'worst_of', 'best_of', 'mod_log']
        session = self.Session()
        server_vars = get_server_ob(ctx, session)
        composite_msg = ""
        for channel_name in channels:
            composite_msg += f"What is the {channel_name} channel?"
            await ctx.send(composite_msg)
            try:
                choice = await self.bot.wait_for('message', check = check_inline, timeout = 30)
            except futures.TimeoutError:
                await ctx.send("No input found, exiting channel config.")
                session.close()
                return
            setattr(server_vars, f"{channel_name}_id", choice.content)
            composite_msg = f"Set {channel_name}'s ID to `{choice.content}`\n"
        await ctx.send(composite_msg)

        verification_msg = ""
        for channel_name in channels:
            id_attr = getattr(server_vars, f"{channel_name}_id")
            verification_msg += f"{channel_name}: `{id_attr}`\n"
        await ctx.send(verification_msg)
        session.close()

    @config.command()
    @commands.is_owner()
    async def globals(self, ctx):
        session = self.Session()
        server_vars = get_server_ob(ctx, session)


def get_server_ob(ctx, session):
    return session.query(Server).filter_by(id=ctx.guild.id).first()



def setup(bot):
    bot.add_cog(Config(bot))
