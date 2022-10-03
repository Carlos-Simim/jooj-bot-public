import csv
import time
import pickle
import disnake
import random
import os

import psycopg2
import requests

from datetime import datetime, timedelta

import roman
from disnake import colour
from disnake.ext import commands, tasks
from github import Github
from riotwatcher import LolWatcher

lol_api = os.getenv('LOL_API')
token = os.getenv('BOT_TOKEN')
cat_api = os.getenv('CAT_API')
github_token = os.getenv('GITHUB_TOKEN')
currency_api = os.getenv('CURRENCY_API')
stock_api = os.getenv('STOCK_API')
version = os.getenv('HEROKU_RELEASE_VERSION')
heroku_database = os.getenv('DATABASE_URL')

changelogs_channel_id = "1019259894676869141"  # ID do canal de changelogs
dono_id = "279678486841524226"  # id do dono do bot
testing_channel_id = "1019257889967325254"  # id do canal de testes
intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", help_command=None, case_insensitive=True, intents=intents)
watcher = LolWatcher(lol_api)  # inicializa o watcher com a api da riot
my_region = 'br1'  # região do bot
aka_brasil = ["bostil", "bananil", "chimpanzil", "cupretil", "cachorril"]  # Sinônimos de brasil
votacoes_ativas = []
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


class Enquete:
    def __init__(self, guild_id, criador, pergunta, mensagem_id):
        self.guild_id = guild_id
        self.sim = 0
        self.nao = 0
        self.voters = []
        self.criador = criador
        self.pergunta = pergunta
        self.mensagem_id = mensagem_id
        self.start_time = datetime.now()


@bot.event  # evento de quando o bot estiver pronto
async def on_ready():
    global dono
    dono = await bot.fetch_user(dono_id)
    random_status.start()
    send_last_commits.start()
    print(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    await dono.send(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    unpickle_enquetes()
    conn = psycopg2.connect(heroku_database, sslmode='require')
    print("BD conectado")


@bot.slash_command(name="enquete", description="Cria uma enquete com uma pergunta de sua escolha.")
async def enquete(ctx, *, pergunta=None):
    global votacoes_ativas
    channel = ctx.channel

    for votacao in votacoes_ativas:
        if votacao.guild_id == ctx.guild.id:
            if pergunta is None:
                try:
                    mensagem = await channel.fetch_message(votacao.mensagem_id)
                    await mensagem.delete()
                except:
                    pass
                embed = disnake.Embed(title=votacao.pergunta, color=0x00ff00)
                embed.add_field(name="Sim", value=votacao.sim, inline=True)
                embed.add_field(name="Não", value=votacao.nao, inline=True)
                await ctx.response.send_message("Enquete ativa enviada abaixo", ephemeral=True)
                nova_mensagem = await channel.send(embed=embed,
                                                   components=[disnake.ui.ActionRow(
                                                       disnake.ui.Button(label="Sim", style=disnake.ButtonStyle.green),
                                                       disnake.ui.Button(label="Não", style=disnake.ButtonStyle.red),
                                                       disnake.ui.Button(label="Encerrar",
                                                                         style=disnake.ButtonStyle.grey))])
                votacao.mensagem_id = nova_mensagem.id
                pickle_enquetes()
                return
            else:
                await ctx.response.send_message("Já existe uma enquete ativa neste servidor", ephemeral=True)
                return
    if pergunta is None:
        await ctx.send(
            "Não há nenhuma enquete ativa neste servidor. Crie uma adicionando uma pergunta no comando /enquete.")
        return

    embed = disnake.Embed(title=pergunta, color=0x00ff00)
    embed.add_field(name="Sim", value=0, inline=True)
    embed.add_field(name="Não", value=0, inline=True)
    mensagem = await channel.send(embed=embed,
                                  components=[disnake.ui.ActionRow(
                                      disnake.ui.Button(label="Sim", style=disnake.ButtonStyle.green),
                                      disnake.ui.Button(label="Não", style=disnake.ButtonStyle.red),
                                      disnake.ui.Button(label="Encerrar",
                                                        style=disnake.ButtonStyle.grey))])
    votacoes_ativas.append(Enquete(ctx.guild.id, ctx.author.id, pergunta, mensagem.id))
    pickle_enquetes()

    await ctx.response.send_message("Votação criada com sucesso! Não esqueça ela aberta :thumbsup:", ephemeral=True)


@bot.event
async def on_button_click(interaction):
    try:
        for votacao in votacoes_ativas:
            if interaction.user.id in votacao.voters and interaction.component.label != "Encerrar" and votacao.guild_id == interaction.guild.id:
                await interaction.response.send_message("Você já votou nesta enquete!", ephemeral=True)
                return

        for votacao in votacoes_ativas:
            if votacao.guild_id == interaction.guild.id:
                votacao.voters.append(interaction.user.id)
                sim = votacao.sim
                nao = votacao.nao
                if interaction.component.label == "Sim":
                    votacao.sim += 1
                    await interaction.response.send_message("Voto computado", ephemeral=True)
                elif interaction.component.label == "Não":
                    votacao.nao += 1
                    await interaction.response.send_message("Voto computado", ephemeral=True)
                elif interaction.component.label == "Encerrar" and (
                        interaction.user.id == votacao.criador or interaction.user.id == int(dono_id)):
                    votacoes_ativas.remove(votacao)
                    await interaction.message.edit(components=[])
                    embed = disnake.Embed(title=f"{interaction.message.embeds[0].title} (Finalizada)")
                    embed.add_field(name="Sim", value=sim, inline=True)
                    embed.add_field(name="Não", value=nao, inline=True)
                    time_var = datetime.now() - votacao.start_time
                    embed.set_footer(text=f"Tempo de votação: {strfdelta(time_var, '{hours}h {minutes}m {seconds}s')}")
                    await interaction.message.edit(embed=embed)
                    pickle_enquetes()
                    return
                else:
                    await interaction.response.send_message("Você não pode encerrar a votação!", ephemeral=True)
                    return
                sim = votacao.sim
                nao = votacao.nao
                pickle_enquetes()

        embed = interaction.message.embeds[0]
        for i in range(len(embed.fields)):
            embed.remove_field(0)

        embed.add_field(name="Sim", value=sim, inline=True)
        embed.add_field(name="Não", value=nao, inline=True)
        await interaction.message.edit(embed=embed)
    except Exception as e:
        await interaction.response.send_message(
            "Ocorreu um erro ao computar seu comando! O erro foi enviado ao desenvolvedor, caso persista no futuro "
            "basta entrar em contato diretamente: Vergil#3489", ephemeral=True)
        print(e)
        await dono.send(e)


def pickle_enquetes():
    with open("enquetes.pickle", "wb") as f:
        pickle.dump(votacoes_ativas, f)


def unpickle_enquetes():
    global votacoes_ativas
    with open("enquetes.pickle", "rb") as f:
        votacoes_ativas = pickle.load(f)


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


@bot.slash_command(name="ipo", description="Mostra os próximos IPOs de empresas. (Initial Public Offering)")
async def ipo(ctx):
    my_list = get_ipo_list()
    embed = disnake.Embed(title="Próximos IPOs", color=disnake.colour.Color.red())
    try:
        print(my_list[1])
    except:
        await ctx.send("Não foi possível encontrar nenhum IPO")
        return
    for i in range(1, len(my_list)):
        embed.add_field(name=my_list[i][0], value=f"Nome: {my_list[i][1]}\n"
                                                  f"Data: {my_list[i][2]}\n"
                                                  f"Exchange: {my_list[i][6]}", inline=True)
    await ctx.send(embed=embed)


def get_ipo_list():
    CSV_URL = f'https://www.alphavantage.co/query?function=IPO_CALENDAR&apikey={stock_api}'
    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        return my_list


@bot.slash_command(name="romano", description="Converte um número para romano e vice-versa")
async def romano(ctx, number):
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
async def romano_error(ctx, error):
    print(error)
    await ctx.send("Um erro desconhecido ocorreu no comando. O erro foi reportado ao dono do bot")
    await dono.send(f"Um erro desconhecido ccorreu no comando:\n{error}")


@bot.slash_command(name="morse", description="Traduz um texto para código morse e vice-versa.")
async def morse(ctx, *, texto):
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
                              '---...': ':', '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-', '..--.-': '_',
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


@bot.slash_command(name="acoes",
                   description="Retorna algumas informações sobre uma determinada ação. Exemplo: TSLA, IBM, NIO, etc.")
async def acoes(ctx, *, acao):
    await ctx.response.defer()
    start = time.perf_counter()
    content, conversao, data_detalhes = get_acoes_info(acao)

    embed = disnake.Embed(title=f"{acao}", color=disnake.Color.blue())
    for item in content:
        date_var = item[0]
        date_var = date_var[8:10] + '/' + date_var[5:7] + '/' + date_var[0:4]
        open_var = float(item[1]['1. open']) * conversao
        open_var = round(open_var, 2)
        high_var = float(item[1]['2. high']) * conversao
        high_var = round(high_var, 2)
        low_var = float(item[1]['3. low']) * conversao
        low_var = round(low_var, 2)
        close_var = float(item[1]['4. close']) * conversao
        close_var = round(close_var, 2)
        embed.add_field(name=f"{date_var}",
                        value=f"Abertura: R${open_var}\nAlta: R${high_var}\nBaixa: R${low_var}\nFechamento: R${close_var}",
                        inline=True)
    embed.add_field(name="Nome", value=data_detalhes['Name'], inline=True)
    embed.add_field(name="Industria", value=data_detalhes['Industry'], inline=True)
    embed.add_field(name="Beta", value=data_detalhes['Beta'], inline=True)

    end = time.perf_counter()
    tempo = round(end - start, 2)
    embed.set_footer(text=f"Tempo de resposta: {tempo} segundos")
    await ctx.send(embed=embed)


def get_acoes_info(acao):
    acao = acao.upper()
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={acao}&apikey={stock_api}'
    r = requests.get(url)
    data = r.json()
    content_temp = data['Time Series (Daily)']
    content_temp = list(content_temp.items())
    conversao = get_conversao("USD", "BRL", 1)
    contador = 0
    content: list = []
    while contador < 12:
        content.append(content_temp[contador])
        contador += 1

    url_detalhes = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={acao}&apikey={stock_api}'
    r_detalhes = requests.get(url_detalhes)
    data_detalhes = r_detalhes.json()

    return content, conversao, data_detalhes


@acoes.error
async def acoes_error(ctx, error):
    print(error)
    await ctx.send("Ação não encontrada.")


def currency_name_to_code(currency_name):
    currency_name = currency_name.upper()
    currency_code = {
        "USD": "USD",
        "DOLAR": "USD",
        "DÓLAR": "USD",
        "REAL": "BRL",
        "BRL": "BRL",
        "EURO": "EUR",
        "EUR": "EUR",
        "LIBRA": "GBP",
        "GBP": "GBP",
        "IENE": "JPY",
        "JPY": "JPY",
        "BITCOIN": "BTC",
        "BTC": "BTC",
        "LITECOIN": "LTC",
        "LTC": "LTC",
        "ETHEREUM": "ETH",
        "ETH": "ETH",
        "XRP": "XRP",
        "RIPPLE": "XRP",
        "CARDANO": "ADA",
        "ADA": "ADA",
        "TETHER": "USDT",
        "USDT": "USDT",
        "BINANCECOIN": "BNB",
        "BNB": "BNB",
        "POLKADOT": "DOT",
        "DOT": "DOT",
        "UNISWAP": "UNI",
        "UNI": "UNI",
        "BITCOINCASH": "BCH",
        "BCH": "BCH",
        "LUMEN": "XLM",
        "XLM": "XLM",
        "CHAINLINK": "LINK",
        "LINK": "LINK",
        "STELLAR": "XLM"
    }
    return currency_code.get(currency_name)


@bot.slash_command(name="moeda", description="Converte uma moeda para outra. Exemplo: 1 dolar para real")
async def converter_moeda(ctx, moeda_origem: str, moeda_destino: str, valor: float):
    await ctx.response.defer()

    try:
        moeda_origem = currency_name_to_code(moeda_origem)
        moeda_destino = currency_name_to_code(moeda_destino)
    except:
        print("Moeda não encontrada.")

    result = get_conversao(moeda_origem, moeda_destino, valor)
    await ctx.send(f"{valor} {moeda_origem} = {round(result * valor, 2)} {moeda_destino}")


def get_conversao(moeda_origem, moeda_destino, valor):
    moeda_origem = moeda_origem.upper()
    moeda_destino = moeda_destino.upper()
    payload = {}
    headers = {
        "apikey": currency_api
    }

    moeda_origem = currency_name_to_code(moeda_origem)
    moeda_destino = currency_name_to_code(moeda_destino)

    url = f"https://api.apilayer.com/exchangerates_data/convert?to={moeda_destino}&from={moeda_origem}&amount={valor}"
    response = requests.request("GET", url, headers=headers, data=payload)
    result = response.json()
    return result['info']['rate']


@converter_moeda.error
async def converter_moeda_error(ctx, error):
    print(error)
    await ctx.send(
        "Um erro desconhecido ocorreu. Tente escrever a moeda corretamente, sem plural ou abreviações. Exemplo: Dólar, Real, Bitcoin, etc."
        "\nCaso o erro persista, utilize o código da moeda por enquanto que em breve era será adicionada a lista de traduções. Exemplo: USD, BRL, BTC, etc.")


@tasks.loop(minutes=5)
async def send_last_commits():
    channel = bot.get_channel(int(changelogs_channel_id))
    testing_channel = bot.get_channel(int(testing_channel_id))
    print("Checking for new commits...")
    commits = get_commits("Carlos-Simim/jooj-bot-public")

    for commit in commits:
        if (commit.commit.author.date - timedelta(hours=3)) > datetime.now() - timedelta(minutes=5):
            embed = disnake.Embed(title=f"Última atualização - {version}",
                                  color=disnake.colour.Color.green())
            embed.add_field(name="Descrição", value=commit.commit.message, inline=False)
            date = commit.commit.author.date - timedelta(hours=3)
            embed.add_field(name="Data", value=(date.strftime("%d/%m/%Y - %H:%M")), inline=False)
            print("Commits enviados")
            await testing_channel.send(embed=embed)
            await channel.send(embed=embed)


def get_commits(repository):
    g = Github(github_token)
    repo = g.get_repo(repository)
    commits = repo.get_commits()
    return commits


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

    if aka_brasil.__contains__(pais.lower()):
        pais = "Brazil"

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
    gato_var = getRandomCat()
    if user is not None:
        await user.send(gato_var)
        await ctx.send("Gato enviado para " + user.name)
        return

    await ctx.send(gato_var)


@bot.slash_command(name="cachorro", description="Retorna um cachorro fofo (muito based).")
async def cachorro(ctx, user: disnake.User = None):
    await ctx.response.defer()
    cachorro_var = getRandomDog()
    if user is not None:
        await user.send(cachorro_var)
        await ctx.send("Cachorro enviado para " + user.name)
        return

    await ctx.send(cachorro_var)


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


@bot.slash_command(name="elos",
                   description="Retorna o ELO + Divisão + Campeão de todos os jogadores de uma partida ativa.")
async def elos(ctx, *, nick: str):
    await ctx.response.defer()
    live_match = get_live_match(nick)

    embedVar = disnake.Embed(title="Elos na partida de {}".format(nick), color=0xff9900)
    for player in live_match['participants']:
        name = player['summonerName']
        champion_name = get_champion_name(player['championId'])

        player_elo_info = watcher.league.by_summoner(my_region, player['summonerId'])

        embedVar.add_field(
            name=f"{name}: {player_elo_info[0]['tier']} {player_elo_info[0]['rank']} ({champion_name})",
            value="\u200b", inline=True)

    await ctx.send(embed=embedVar)


@elos.error
async def elos_error(ctx, error):
    await ctx.send(f'Não foi possível encontrar a partida de ``{ctx.options["nick"]}``')
    await dono.send(error)


def get_live_match(nick):
    me = getSummonerByName(nick)
    return watcher.spectator.by_summoner(region=my_region, encrypted_summoner_id=me['id'])


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


def get_rune_name(rune_name):
    url = "http://ddragon.leagueoflegends.com/cdn/12.16.1/data/en_US/runesReforged.json"
    response = requests.get(url)
    runas_dicionário: dict = {"Dark Harvest": "Colheita Sombria", "Electrocute": "Eletrocutar", "Predator": "Predador",
                              "Hail of Blades": "Chuva de Lâminas", "Summon Aery": "Aery", "Arcane Comet": "Cometa",
                              "Phase Rush": "Ímpeto", "Lethal Tempo": "Ritmo Fatal", "Grasp of the Undying": "Grasp",
                              "Aftershock": "Pós-Choque", "Glacial Augment": "Gelinho", "Unsealed Spellbook": "Livro"}

    for rune_tree in response.json():
        for rune_var in rune_tree['slots']:
            for runes in rune_var['runes']:
                if runes['id'] == rune_name:
                    return runas_dicionário.get(runes['name'])

    return "Runa não encontrada"


@bot.slash_command(name="perfil",
                   description="Retorna algumas informações do perfil da pessoa e da última partida jogada.")
async def perfil(ctx, *, nick: str):
    await ctx.response.defer()
    global derrotas, vitorias, kills, deaths, assists, pings, drags, pick, lane, dano, killingspree, visao, red, green, rank, tier, final_bool, winrate, pdl, queue_name, farm, barons, \
        final, ultima_atualizacao, control_wards, rune, dano_estruturas
    red = colour.Color.red()
    green = colour.Color.green()
    me, league_info, last_match = get_matches_info(nick)

    for thing in league_info:
        if thing['queueType'] == 'RANKED_SOLO_5x5':
            vitorias = thing['wins']
            derrotas = thing['losses']
            rank = thing['rank']
            tier = thing['tier']
            pdl = thing['leaguePoints']

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
            control_wards = player['visionWardsBoughtInGame']
            rune_name = player['perks']['styles'][0]['selections'][0]['perk']
            rune = get_rune_name(rune_name)
            dano_estruturas = player['damageDealtToObjectives']

    if final_bool is True:
        final = 'Vitória'
    else:
        final = 'Derrota'

    winrate = vitorias / (vitorias + derrotas) * 100
    winrate = round(winrate, 2)

    ultima_atualizacao = ultima_atualizacao.strftime("%d/%m/%Y %H:%M")

    tier = get_translation_stats(tier)
    lane = get_translation_stats(lane)

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
    embedVar.add_field(name="Wards compradas", value=control_wards, inline=True)
    embedVar.add_field(name="Runa Primária", value=rune, inline=True)
    embedVar.add_field(name="Dano a estruturas", value=dano_estruturas, inline=True)
    embedVar.add_field(name="Resultado", value=final, inline=True)
    embedVar.add_field(name="Última partida jogada", value=ultima_atualizacao, inline=True)
    embedVar.set_thumbnail(
        url="https://opgg-static.akamaized.net/images/profile_icons/profileIcon" + str(me['profileIconId']) + ".jpg")

    await ctx.send(embed=embedVar)


def get_matches_info(nick):
    me = getSummonerByName(nick)
    league_info = watcher.league.by_summoner(my_region, me['id'])
    my_matches = watcher.match.matchlist_by_puuid(my_region, me['puuid'])
    last_match = watcher.match.by_id(my_region, my_matches[0])
    return me, league_info, last_match


@perfil.error
async def perfil_error(ctx, error):
    await ctx.send(
        "Erro inesperado ao buscar informações do jogador. Verifique se o nick está correto e tente novamente, tente novamente mais tarde caso o problema persista.")
    await dono.send(f"Erro inesperado ao buscar informações de algum jogador, verifique os logs do bot. Erro: {error}")


bot.load_extension("minesweeper")
bot.load_extension("dice")
bot.run(token)
