import discord
from discord.ext import commands
import sqlalchemy
from sqlalchemy.orm import sessionmaker

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load the cog commands into the bot.
        # for command in Config.get_commands(self):

    # The config group of commands.
    @commands.group(name="config",
               invoke_without_command=True,
               help="The group of config commands.")
    @commands.is_owner()
    async def config(self, ctx):
        await ctx.send("You should check your parameters, chef.")

    # Sets the number of upvotes for best_of.
    @config.command(name="set_upvotes",
                      help = "Sets the number of upvotes required for best_of in the server",
                      brief = "Sets upvotes for the memes channel.")
    @commands.is_owner()
    async def set_upvotes(self, ctx, upvotes):
        await ctx.send("upvotes... set. Pretend they did.")



def setup(bot):
    bot.add_cog(Config(bot))
