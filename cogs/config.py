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
        server_object = Server(id = ctx.guild.id)
        try:
            session.add(server_object)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            await ctx.send(session.query(Server).filter_by(id=ctx.guild.id).first().id)
            session.close()
            await ctx.send("This server has already been created in the database.")
            return
        except:
            session.rollback()
            session.close()
            await ctx.send("Something went horribly wrong.")
            return
        session.close()
        await ctx.send(f"Server {ctx.guild.name} added to the database.")

    # Sets the number of upvotes for best_of.
    @config.command(name="set_upvotes",
                      help = "Sets the number of upvotes required for best_of in the server",
                      brief = "Sets upvotes for the memes channel.")
    @commands.is_owner()
    async def set_upvotes(self, ctx, upvote_count):
        session = self.Session()
        server_object = session.query(Server).filter_by(id=ctx.guild.id).first()
        server_object.upvotes = upvote_count
        session.close()
        await ctx.send("upvotes... set. Maybe?")



def setup(bot):
    bot.add_cog(Config(bot))
