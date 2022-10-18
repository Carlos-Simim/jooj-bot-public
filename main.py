import os
import disnake
import psycopg2

from datetime import datetime, timedelta
from disnake.ext import commands
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
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name="Você através da sua webcam"))
    await send_last_commits()
    print(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    await dono.send(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    data_read()


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

    print("Commits enviados")


def get_commits(repository):
    g = Github(github_token)
    repo = g.get_repo(repository)
    commits = repo.get_commits()
    return commits


def data_read():
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


bot.load_extension("minesweeper")
bot.load_extension("dice")
bot.load_extension("traducoes")
bot.load_extension("paises")
bot.load_extension("lol")
bot.load_extension("diversos")
bot.load_extension("economia")
bot.load_extension("enquetes")
bot.run(token)
