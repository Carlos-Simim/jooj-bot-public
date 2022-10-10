from main import *
from disnake.ext import commands


class diversos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ping", description="Retorna o ping do bot.")
    async def ping(self, ctx):
        await ctx.send(f'Latência de: {round(bot.latency * 1000)}ms')

    @commands.slash_command(name="fato", description="Retorna um fato aleatório em inglês")
    async def fato(self, ctx):
        await ctx.response.defer()
        await ctx.send(getRandomFact())

    @commands.slash_command(name="coinflip", description="Joga uma moeda (cara ou coroa)")
    async def coinflip(self, ctx):
        await ctx.send('**Cara** :speaking_head:' if random.randint(0, 1) == 0 else '**Coroa** :crown:')

    @commands.slash_command(name="gato", description="Retorna um gato fofo (muito based).")
    async def gato(self, ctx, user: disnake.User = None):
        await ctx.response.defer()
        gato_var = getRandomCat()
        if user is not None:
            await user.send(gato_var)
            await ctx.send("Gato enviado para " + user.name)
            return

        await ctx.send(gato_var)

    @commands.slash_command(name="cachorro", description="Retorna um cachorro fofo (muito based).")
    async def cachorro(self, ctx, user: disnake.User = None):
        await ctx.response.defer()
        cachorro_var = getRandomDog()
        if user is not None:
            await user.send(cachorro_var)
            await ctx.send("Cachorro enviado para " + user.name)
            return

        await ctx.send(cachorro_var)

    @commands.slash_command(name="limpar", description="Limpa as últimas N mensagens no chat que for usado.")
    async def limpar(self, ctx, quantidade: int):
        if ctx.author.guild_permissions.administrator:
            await ctx.channel.purge(limit=int(quantidade))
            await ctx.send(f"{ctx.author.mention} limpou ``{quantidade}`` mensagens!")
        else:
            msg = "Você não tem permissão para utilizar esse comando."
            await ctx.send(msg)

    @commands.slash_command(name="avatar", description="Retorna seu próprio avatar ou de algum outro usuário.")
    async def avatar(self, ctx, user: disnake.User = None):
        if user is not None:
            embedVar = disnake.Embed(title="Avatar de " + user.name, color=0x00ff00)
            embedVar.set_image(url=user.avatar.url)
            await ctx.send(embed=embedVar)
            return

        try:
            embedVar = disnake.Embed(title="Seu avatar", color=0x00ff00)
            embedVar.set_image(url=ctx.author.avatar.url)
            await ctx.send(embed=embedVar)
        except:
            await ctx.send("Você não tem avatar.")

    @commands.slash_command(name='oi', description='Pra caso você esteja carente :)')
    async def oi(self, ctx):
        print('oi')
        await ctx.send(ctx.author.mention + " oi! :heart:")


def getRandomFact():
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    response = requests.get(url)
    return response.json()["text"]


def getRandomCat():
    url = "https://api.thecatapi.com/v1/images/search"
    response = requests.get(url, params={"x-api-key": cat_api})
    return response.json()[0]["url"]


def getRandomDog():
    url = "https://api.thedogapi.com/v1/images/search"
    response = requests.get(url)
    return response.json()[0]["url"]


def setup(bot):
    bot.add_cog(diversos(bot))
