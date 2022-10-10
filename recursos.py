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
from changelogs import send_last_commits

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