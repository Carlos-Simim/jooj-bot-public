import os
import disnake
import random
import requests

from datetime import datetime, timedelta
from disnake import colour
from disnake.ext import commands, tasks
from github import Github
from riotwatcher import LolWatcher

lol_api = os.environ['LOL_API']
token = os.environ['BOT_TOKEN']
cat_api = os.environ['CAT_API']
github_token = os.environ['GITHUB_TOKEN']
changelogs_channel_id = "1019259894676869141" # ID do canal de changelogs
dono_id = "279678486841524226"  # id do dono do bot
testing_channel_id = "1019257889967325254"  # id do canal de testes
intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", help_command=None, case_insensitive=True, intents=intents)
watcher = LolWatcher(lol_api)  # inicializa o watcher com a api da riot
my_region = 'br1'  # região do bot
aka_brasil = ["bostil", "bananil", "chimpanzil", "cupretil", "cachorril"]  # Sinônimos de brasil

morse_code = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '0': '-----', ', ': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.',
    '-': '-....-', '(': '-.--.', ')': '-.--.-', ' ': ' / '
}


@bot.event  # evento de quando o bot estiver pronto
async def on_ready():
    global dono
    dono = await bot.fetch_user(dono_id)
    random_status.start()
    send_last_commits.start()
    print(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    await dono.send(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


@bot.slash_command(name="morse", description="Traduz um texto para código morse e vice-versa.")
async def morse(ctx, *, texto):
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
                              '---...': ':', '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-', '..--.-': '_',
                              '.-..-.': '"', '...-..-': '$', '.--.-.': '@', '...---...': 'SOS', '/': ' '}

    if texto.count('.') == 0 and texto.count('-') == 0:
        texto = texto.upper()
        for letra in texto:
            try:
                texto_morse += morse_code.get(letra) + ' '
            except TypeError:
                texto_morse += letra + ' '
        await ctx.send(content=texto_morse)
    else:
        for letra in texto.split():
            try:
                texto_normal += morse_dicionario.get(letra)
            except TypeError:
                texto_normal += letra
        texto_normal = texto_normal.upper()
        await ctx.send(content=texto_normal)


@tasks.loop(minutes=5)
async def send_last_commits():
    channel = bot.get_channel(int(changelogs_channel_id))
    testing_channel = bot.get_channel(int(testing_channel_id))
    g = Github(github_token)
    print("Checking for new commits...")
    repo = g.get_repo("Carlos-Simim/jooj-bot-public")
    commits = repo.get_commits()
    for commit in commits:
        if (commit.commit.author.date - timedelta(hours=3)) > datetime.now() - timedelta(minutes=5):
            embed = disnake.Embed(title=f"Última atualização - v{commits.totalCount}", color=disnake.colour.Color.green())
            embed.add_field(name="Descrição", value=commit.commit.message, inline=False)
            embed.add_field(name="Data", value=(commit.commit.author.date - timedelta(hours=3)), inline=False)
            print("Commits enviados")
            await testing_channel.send(embed=embed)
            await channel.send(embed=embed)


# TODO - Arrumar comando pra gerar polls
@bot.slash_command(name="poll", description="Cria uma enquete de 0 a 4 opções - Ainda não funciona")
async def poll(self, ctx, question: str, option1: str = None, option2: str = None, option3: str = None,
               option4: str = None):
    if option1 is None and option2 is None and option3 is None and option4 is None:
        embed = get_poll_embed(question)
        # send embed with reactions
        print(await ctx.send(embed=embed))
        print()


def get_poll_embed(question):
    embed = disnake.Embed(title=question, color=disnake.colour.Color.red())
    return embed


@tasks.loop(seconds=180)
async def random_status():
    lista_filmes = ["Morbius", "Esquadrão Suicida 1", "Death Note Netflix", "Birdemic", "Venom", "Pinóquio novo",
                    "Mulher Maravilha 1984"]
    random_number = random.randint(0, len(lista_filmes) - 1)
    await bot.change_presence(
        activity=disnake.Activity(type=disnake.ActivityType.watching, name=lista_filmes[random_number]))


@bot.slash_command(name="pais", description="Retorna informações sobre um país")
async def pais(ctx, *, pais: str):
    await ctx.response.defer()
    for word in aka_brasil:
        if pais.lower() == word:
            pais = "Brazil"
            break
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
    pais_dicionario: dict = {"capital": pais["capital"][0], "populacao": pais["population"], "area": pais["area"],
                             "mapa": pais["maps"]["googleMaps"], "street_view": pais["maps"]["openStreetMaps"],
                             "un_member": pais["unMember"],
                             "continente": get_translation_pais(pais["continents"][0]),
                             "litoral": pais["landlocked"], "lado_transito": pais["car"]["side"],
                             "dia_semana": get_translation_pais(pais["startOfWeek"]),
                             "brasao_armas": pais["coatOfArms"]["png"], "bandeira": pais["flag"]}

    return pais_dicionario


@bot.slash_command(name="ping", description="Retorna o ping do bot.")
async def ping(ctx):
    await ctx.send(f'Latência de: {round(bot.latency * 1000)}ms')


@bot.slash_command(name="fato", description="Retorna um fato aleatório em inglês")
async def fato(ctx):
    await ctx.response.defer()
    await ctx.send(getRandomFact())


def getRandomFact():
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    response = requests.get(url)
    return response.json()["text"]


def getSummonerByName(name):
    return watcher.summoner.by_name(my_region, name)


@bot.slash_command(name="coinflip", description="Joga uma moeda (cara ou coroa)")
async def coinflip(ctx):
    await ctx.send('**Cara** :speaking_head:' if random.randint(0, 1) == 0 else '**Coroa** :crown:')


@bot.slash_command(name="gato", description="Retorna um gato fofo (muito based).")
async def gato(ctx, user: disnake.User = None):
    await ctx.response.defer()
    if user is not None:
        await user.send(getRandomCat())
        await ctx.send("Gato enviado para " + user.name)
        return

    await ctx.send(getRandomCat())


@bot.slash_command(name="cachorro", description="Retorna um cachorro fofo (muito based).")
async def cachorro(ctx, user: disnake.User = None):
    await ctx.response.defer()
    if user is not None:
        await user.send(getRandomDog())
        await ctx.send("Cachorro enviado para " + user.name)
        return

    await ctx.send(getRandomDog())


def getRandomCat():
    url = "https://api.thecatapi.com/v1/images/search"
    response = requests.get(url, params={"x-api-key": cat_api})
    return response.json()[0]["url"]


def getRandomDog():
    url = "https://api.thedogapi.com/v1/images/search"
    response = requests.get(url)
    return response.json()[0]["url"]


@bot.slash_command(name="limpar", description="Limpa as últimas N mensagens no chat que for usado.")
async def limpar(ctx, quantidade: int):
    await ctx.send("Limpando mensagens...")
    if ctx.author.guild_permissions.administrator:
        await ctx.channel.purge(limit=int(quantidade))
        await ctx.send(f"{ctx.author.mention} limpou ``{quantidade}`` mensagens!")
    else:
        msg = "Você não tem permissão para utilizar esse comando."
        await ctx.send(msg)


@bot.slash_command(name="avatar", description="Retorna seu próprio avatar ou de algum outro usuário.")
async def avatar(ctx, user: disnake.User = None):
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


@bot.slash_command(name="elos", description="Retorna o ELO + Divisão + Campeão de todos os jogadores de uma partida ativa.")
async def elos(ctx, *, nick: str):
    await ctx.response.defer()
    me = getSummonerByName(nick)
    embedVar = disnake.Embed(title="Elos na partida de {}".format(nick), color=0xff9900)

    try:
        live_match = watcher.spectator.by_summoner(region=my_region, encrypted_summoner_id=me['id'])
    except:
        await ctx.send('O jogador não está em nenhuma partida no momento, ou você informou um nick inválido.')
        return

    else:
        for player in live_match['participants']:
            name = player['summonerName']
            champion_name = get_champion_name(player['championId'])

            player_elo_info = watcher.league.by_summoner(my_region, player['summonerId'])

            embedVar.add_field(
                name=f"{name}: {player_elo_info[0]['tier']} {player_elo_info[0]['rank']} ({champion_name})",
                value="\u200b", inline=True)

        await ctx.send(embed=embedVar)
        return


@bot.slash_command(name='oi', description='Pra caso você esteja carente :)')
async def oi(ctx):
    print('oi')
    await ctx.send(ctx.author.mention + " oi! :heart:")


def get_champion_name(champion_id):
    url = 'http://ddragon.leagueoflegends.com/cdn/12.16.1/data/en_US/champion.json'
    response = requests.get(url)
    champions = response.json()['data']
    for champion in champions:
        if champions[champion]['key'] == str(champion_id):
            return champions[champion]['name']
    return 'Champion not found'


def get_queue_name(queue_id):
    url = "https://static.developer.riotgames.com/docs/lol/queues.json"
    response = requests.get(url)
    queue_name = ''

    for queue in response.json():
        if queue["queueId"] == queue_id:
            queue_name = queue["description"]

    if queue_name == '5v5 Ranked Solo games':
        queue_name = 'Solo/Duo'
    if queue_name == '5v5 Ranked Flex games':
        queue_name = 'Flex'
    if queue_name == '5v5 ARAM games':
        queue_name = 'ARAM'
    if queue_name == '5v5 Blind Pick games':
        queue_name = 'Normal'

    return queue_name


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


def get_translation_stats(word):
    stats_dicionario: dict = {"IRON": "Ferro", "BRONZE": "Bronze", "SILVER": "Prata", "GOLD": "Ouro",
                              "PLATINUM": "Platina",
                              "DIAMOND": "Diamante", "MASTER": "Mestre", "GRANDMASTER": "Grão Mestre",
                              "CHALLENGER": "Desafiante",
                              "TOP": "Topo", "JUNGLE": "Jungle", "MIDDLE": "Meio", "BOTTOM": "ADC",
                              "SUPPORT": "Suporte"}

    return stats_dicionario.get(word)


def get_stats_embed(nick):
    if final_bool:
        embedVar = disnake.Embed(title="Estatísticas de " + nick, color=green)
    else:
        embedVar = disnake.Embed(title="Estatísticas de " + nick, color=red)

    embedVar.add_field(name="Vitórias", value=vitorias, inline=True)
    embedVar.add_field(name="Derrotas", value=derrotas, inline=True)
    embedVar.add_field(name="Winrate", value=str(winrate) + "%", inline=True)
    embedVar.add_field(name=f"{tier} {rank} ({pdl} pdl)", inline=False,
                       value='=====================')
    embedVar.add_field(name="Última partida:", value="\u200b", inline=False)
    embedVar.add_field(name="Kills", value=kills, inline=True)
    embedVar.add_field(name="Deaths", value=deaths, inline=True)
    embedVar.add_field(name="Assists", value=assists, inline=True)
    embedVar.add_field(name="Pings", value=pings, inline=True)
    embedVar.add_field(name="Dragões", value=drags, inline=True)
    embedVar.add_field(name="Barons", value=barons, inline=True)
    embedVar.add_field(name="Pick", value=pick, inline=True)
    embedVar.add_field(name="Lane", value=lane, inline=True)
    embedVar.add_field(name="Dano", value=dano, inline=True)
    embedVar.add_field(name="Killing spree", value=killingspree, inline=True)
    embedVar.add_field(name="Tipo da fila", value=queue_name, inline=True)
    embedVar.add_field(name="Farm", value=farm, inline=True)
    embedVar.add_field(name="Visão", value=visao, inline=True)
    embedVar.add_field(name="Resultado", value=final, inline=True)
    embedVar.add_field(name="Última partida jogada", value=ultima_atualizacao, inline=True)
    embedVar.set_thumbnail(
        url="https://opgg-static.akamaized.net/images/profile_icons/profileIcon" + str(me['profileIconId']) + ".jpg")

    return embedVar


@bot.slash_command(name="perfil",
                   description="Retorna algumas informações do perfil da pessoa e da última partida jogada.")
async def perfil(ctx, *, nick: str):
    await ctx.response.defer()

    global derrotas, vitorias, kills, deaths, assists, pings, drags, pick, lane, dano, killingspree, visao, red, green, rank, tier, final_bool, winrate, pdl, queue_name, farm, barons, \
        final, ultima_atualizacao

    red = colour.Color.red()
    green = colour.Color.green()

    global me
    me = getSummonerByName(nick)

    league_info = watcher.league.by_summoner(my_region, me['id'])

    for thing in league_info:
        if thing['queueType'] == 'RANKED_SOLO_5x5':
            vitorias = thing['wins']
            derrotas = thing['losses']
            rank = thing['rank']
            tier = thing['tier']
            pdl = thing['leaguePoints']

    my_matches = watcher.match.matchlist_by_puuid(my_region, me['puuid'])
    last_match = watcher.match.by_id(my_region, my_matches[0])
    time_stamp = last_match['info']['gameEndTimestamp']
    ultima_atualizacao = datetime.fromtimestamp(time_stamp / 1000)

    for player in last_match['info']['participants']:
        if player['summonerId'] == me['id']:
            kills = player['kills']
            deaths = player['deaths']
            assists = player['assists']
            pings = player['basicPings']
            drags = player['dragonKills']
            pick = player['championName']
            lane = player['teamPosition']
            dano = player['totalDamageDealtToChampions']
            killingspree = player['largestKillingSpree']
            visao = player['visionScore']
            final_bool = player['win']
            queue_name = get_queue_name(last_match['info']['queueId'])
            barons = player['baronKills']
            farm = player['totalMinionsKilled']

    if final_bool is True:
        final = 'Vitória'
    else:
        final = 'Derrota'

    winrate = vitorias / (vitorias + derrotas) * 100
    winrate = round(winrate, 2)

    ultima_atualizacao = ultima_atualizacao.strftime("%d/%m/%Y %H:%M")

    tier = get_translation_stats(tier)
    lane = get_translation_stats(lane)

    embedVar = get_stats_embed(nick)

    await ctx.send(embed=embedVar)


@perfil.error
async def perfil_error(ctx, error):
    await ctx.send(
        "Erro inesperado ao buscar informações do jogador. Verifique se o nick está correto e tente novamente, tente novamente mais tarde caso o problema persista.")
    await dono.send(f"Erro inesperado ao buscar informações de algum jogador, verifique os logs do bot. Erro: {error}")


bot.load_extension("minesweeper")
bot.load_extension("dice")
bot.run(token)