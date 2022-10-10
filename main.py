import csv
import time
import roman
import disnake
import random
import os
import psycopg2
import requests

from datetime import datetime, timedelta
from disnake import colour
from disnake.ext import commands, tasks
from github import Github
from riotwatcher import LolWatcher
from uuid import uuid4

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
bot = commands.Bot(help_command=None, case_insensitive=True, intents=intents)
watcher = LolWatcher(lol_api)  # inicializa o watcher com a api da riot
my_region = 'br1'  # região do bot
aka_brasil = ["bostil", "bananil", "chimpanzil", "cupretil", "cachorril"]  # Sinônimos de brasil
votacoes_ativas = []
my_database = psycopg2.connect(heroku_database, sslmode='require')
dono: disnake.User = None
test_guild = [1007317177520619610]
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
        self.enquete_id = uuid4()


@bot.event  # evento de quando o bot estiver pronto
async def on_ready():
    global dono
    dono = await bot.fetch_user(dono_id)
    random_status.start()
    send_last_commits.start()
    print(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    await dono.send(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    # Leitura de dados do banco de dados
    cursor = my_database.cursor()
    cursor2 = my_database.cursor()
    cursor.execute("SELECT * FROM public.\"Enquetes\"")
    for row in cursor.fetchall():
        enquete = Enquete(row[0], row[3], row[4], row[5])
        enquete.sim = row[1]
        enquete.nao = row[2]
        enquete.enquete_id = row[6]
        votacoes_ativas.append(enquete)
        cursor2.execute(f"SELECT * FROM public.\"Voters\" WHERE enquete_id=\'{enquete.enquete_id}\'")
        for row2 in cursor2.fetchall():
            enquete.voters.append(row2[0])
    cursor2.close()
    cursor.close()


def inserir_enquete(ctx):
    cursor = my_database.cursor()
    for enquete in votacoes_ativas:
        if enquete.guild_id == ctx.guild.id:
            query = f"INSERT INTO public.\"Enquetes\" (enquete_id, guild_id, sim, nao, criador, pergunta, mensagem_id) VALUES (\'{enquete.enquete_id}\', {enquete.guild_id}, {enquete.sim}, {enquete.nao}, {enquete.criador}, \'{enquete.pergunta}\', {enquete.mensagem_id})"
            print(query)
            cursor.execute(query)
    my_database.commit()
    cursor.close()


def inserir_voters(votacao):
    cursor = my_database.cursor()
    cursor2 = my_database.cursor()
    cursor2.execute(f"SELECT * FROM public.\"Voters\" WHERE enquete_id=\'{votacao.enquete_id}\'")
    voters_temp = []
    # Lista com os voters já existentes do banco de dados. Para verificar se existe a necessidade de adicionar um novo voter para aquela votação no banco de dados
    for row in cursor2.fetchall():
        voters_temp.append(row[0])
    cursor2.close()

    for voter in votacao.voters:
        if voter not in voters_temp:
            query = f"INSERT INTO public.\"Voters\" (enquete_id, user_id) VALUES (\'{votacao.enquete_id}\', {voter})"
            print(query)
            cursor.execute(query)
    query = f'UPDATE public.\"Enquetes\" SET sim={votacao.sim}, nao={votacao.nao} WHERE enquete_id=\'{votacao.enquete_id}\''
    print(query)
    cursor.execute(query)
    my_database.commit()
    cursor.close()


def atualizar_mensagem(votacao):
    cursos = my_database.cursor()
    query = f'UPDATE public.\"Enquetes\" SET mensagem_id={votacao.mensagem_id} WHERE enquete_id=\'{votacao.enquete_id}\''
    print(query)
    cursos.execute(query)
    my_database.commit()
    cursos.close()


def remover_enquete(votacao):
    cursor = my_database.cursor()
    query = f'DELETE FROM public.\"Enquetes\" WHERE enquete_id=\'{votacao.enquete_id}\''
    print(query)
    cursor.execute(query)
    query = f'DELETE FROM public.\"Voters\" WHERE enquete_id=\'{votacao.enquete_id}\''
    print(query)
    cursor.execute(query)
    my_database.commit()
    cursor.close()


@bot.slash_command(name="enquete", description="Cria uma enquete com uma pergunta de sua escolha.")
async def enquete(ctx, *, pergunta=None):
    global votacoes_ativas
    channel = ctx.channel

    for votacao in votacoes_ativas:
        if votacao.guild_id == str(ctx.guild.id):
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
                atualizar_mensagem(votacao)
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
    inserir_enquete(ctx)

    await ctx.response.send_message("Votação criada com sucesso! Não esqueça ela aberta :thumbsup:", ephemeral=True)


@bot.event
async def on_button_click(interaction):
    try:
        for votacao in votacoes_ativas:
            if str(interaction.user.id) in votacao.voters and interaction.component.label != "Encerrar" and int(
                    votacao.guild_id) == interaction.guild.id:
                await interaction.response.send_message("Você já votou nesta enquete!", ephemeral=True)
                return

        for votacao in votacoes_ativas:
            if int(votacao.guild_id) == interaction.guild.id:
                votacao.voters.append(str(interaction.user.id))
                sim = votacao.sim
                nao = votacao.nao
                if interaction.component.label == "Sim":
                    votacao.sim += 1
                    await interaction.response.send_message("Voto computado", ephemeral=True)
                elif interaction.component.label == "Não":
                    votacao.nao += 1
                    await interaction.response.send_message("Voto computado", ephemeral=True)
                elif interaction.component.label == "Encerrar" and (
                        interaction.user.id == int(votacao.criador) or interaction.user.id == int(dono_id)):
                    votacoes_ativas.remove(votacao)
                    await interaction.message.edit(components=[])
                    embed = disnake.Embed(title=f"{interaction.message.embeds[0].title} (Finalizada)")
                    embed.add_field(name="Sim", value=sim, inline=True)
                    embed.add_field(name="Não", value=nao, inline=True)
                    time_var = datetime.now() - votacao.start_time
                    embed.set_footer(text=f"Tempo de votação: {strfdelta(time_var, '{hours}h {minutes}m {seconds}s')}")
                    await interaction.message.edit(embed=embed)
                    remover_enquete(votacao)
                    return
                else:
                    await interaction.response.send_message("Você não pode encerrar a votação!", ephemeral=True)
                    return
                sim = votacao.sim
                nao = votacao.nao
                inserir_voters(votacao)

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


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


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


bot.load_extension("minesweeper")
bot.load_extension("dice")
bot.load_extension("traducoes")
bot.load_extension("paises")
bot.load_extension("lol")
bot.load_extension("diversos")
bot.load_extension("economia")
bot.run(token)
