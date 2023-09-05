import random

from disnake.ext import commands


class dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="d", description="Rola um dado de quantos lados você quiser.")
    async def d(self, ctx, lados: int):
        if lados <= 1:
            await ctx.send(f'{ctx.author.mention}, um dado não pode ter lados negativos, eu heim.')
            return
        if lados == 2:
            await ctx.send(f'{ctx.author.mention}, um dado de 2 lados é uma moeda, use o /coinflip. :rolling_eyes:')
            return
        resultado = random.randint(1, lados)
        await ctx.send(f'{ctx.author.mention} rolou um d{lados}! Resultado: ``{resultado}``')


def setup(bot):
    bot.add_cog(dice(bot))
