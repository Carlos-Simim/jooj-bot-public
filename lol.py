import main
from disnake.ext import commands
test_guild = [1007317177520619610]


class lol(commands.Cog):
    def __init__(self, bot):
        self.bot = bot




def setup(bot):
    bot.add_cog(lol(bot))
