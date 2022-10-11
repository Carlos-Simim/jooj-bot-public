import roman

from main import *
from disnake.ext import commands


class traducoes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="romano", description="Converte um número para romano e vice-versa")
    async def romano(self, ctx, number):
        if number.isdigit():
            number = int(number)
            if number > 4999:
                await ctx.send("O número não pode ser maior que 4999")
                return
            else:
                await ctx.send(f"{number} = {roman.toRoman(number)}")
        else:
            await ctx.send(f"{number} = {roman.fromRoman(number)}")

    @romano.error
    async def romano_error(self, ctx, error):
        print(error)
        await ctx.send("Um erro desconhecido ocorreu no comando. O erro foi reportado ao dono do bot")
        await dono.send(f"Um erro desconhecido ccorreu no comando:\n{error}")

    @commands.slash_command(name="morse", description="Traduz um texto para código morse e vice-versa.")
    async def morse(self, ctx, *, texto):
        await ctx.send(get_morse_translation(texto))


def get_morse_translation(texto):
    texto = texto.lower()
    texto_morse = ''
    texto_normal = ''
    morse_dicionario: dict = {'.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e', '..-.': 'f', '--.': 'g',
                              '....': 'h', '..': 'i', '.---': 'j', '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n',
                              '---': 'o', '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't', '..-': 'u',
                              '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y', '--..': 'z', '.----': '1',
                              '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
                              '---..': '8', '----.': '9', '-----': '0', '.-.-.-': '.', '--..--': ',', '..--..': '?',
                              '.----.': "'", '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')', '.-...': '&',
                              '---...': ':', '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-',
                              '..--.-': '_',
                              '.-..-.': '"', '...-..-': '$', '.--.-.': '@', '...---...': 'SOS', '/': ' '}
    if texto.count('.') == 0 and texto.count('-') == 0:
        texto = texto.upper()
        for letra in texto:
            try:
                texto_morse += morse_code.get(letra) + ' '
            except TypeError:
                texto_morse += letra + ' '
        return texto_morse
    else:
        for letra in texto.split():
            try:
                texto_normal += morse_dicionario.get(letra)
            except TypeError:
                texto_normal += letra
        texto_normal = texto_normal.upper()
        return texto_normal


def setup(bot):
    bot.add_cog(traducoes(bot))
