import requests

from main import *
from disnake.ext import commands


class paises(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="pais", description="Retorna informações sobre um país")
    async def pais(self, ctx, *, pais: str):
        await ctx.response.defer()
        pais = pais.lower()

        try:
            info = getPaisInfo(pais)
        except:
            await ctx.send("Não consegui encontrar esse país!")
            return

        embedVar = disnake.Embed(title="Informações de " + pais, color=0x00ff00)
        embedVar.add_field(name="Capital", value=info.get("capital"), inline=True)
        embedVar.add_field(name="População", value=str(info.get("populacao")) + " hab.", inline=True)
        embedVar.add_field(name="Área", value=str(info.get("area")) + "km²", inline=True)

        if info.get("un_member"):
            embedVar.add_field(name="Membro da ONU", value=":white_check_mark:", inline=True)
        else:
            embedVar.add_field(name="Membro da ONU", value=":x:", inline=True)

        embedVar.add_field(name="Continente", value=info.get("continente"), inline=True)

        if not info.get("litoral"):
            embedVar.add_field(name="Possui Litoral", value=":white_check_mark:", inline=True)
        else:
            embedVar.add_field(name="Possui Litoral", value=":x:", inline=True)

        if info.get("lado_transito") == "left":
            embedVar.add_field(name="Lado do trânsito", value=":leftwards_arrow_with_hook:", inline=True)
        else:
            embedVar.add_field(name="Lado do trânsito", value=":arrow_right:", inline=True)

        embedVar.add_field(name="1° Dia da semana", value=info.get("dia_semana"), inline=True)
        embedVar.add_field(name="Bandeira", value=info.get("bandeira"), inline=True)
        embedVar.set_thumbnail(url=info.get("brasao_armas"))

        await ctx.send(embed=embedVar)


def getPaisInfo(paisVar):
    url = "https://restcountries.com/v3.1/name/" + paisVar
    response = requests.get(url)
    pais = response.json()[0]
    # pega as informações do país da API e coloca em um dicionário
    pais_dicionario: dict = {"capital": pais["capital"][0], "populacao": pais["population"],
                             "area": pais["area"],
                             "mapa": pais["maps"]["googleMaps"],
                             "street_view": pais["maps"]["openStreetMaps"],
                             "un_member": pais["unMember"],
                             "continente": get_translation_pais(pais["continents"][0]),
                             "litoral": pais["landlocked"], "lado_transito": pais["car"]["side"],
                             "dia_semana": get_translation_pais(pais["startOfWeek"]),
                             "brasao_armas": pais["coatOfArms"]["png"], "bandeira": pais["flag"]}

    return pais_dicionario


def get_translation_pais(word):
    pais_traducao_dicionario: dict = {"monday": "Segunda-feira", "tuesday": "Terça-feira", "wednesday": "Quarta-feira",
                                      "thursday": "Quinta-feira", "friday": "Sexta-feira", "saturday": "Sábado",
                                      "sunday": "Domingo",
                                      "South America": "América do Sul", "North America": "América do Norte",
                                      "Europe": "Europa",
                                      "Oceania": "Oceania", "Asia": "Ásia", "Africa": "África", "Americas": "Américas",
                                      "Central America": "América Central",
                                      "antartica": "Antártida"}

    return pais_traducao_dicionario.get(word)


def setup(bot):
    bot.add_cog(paises(bot))
