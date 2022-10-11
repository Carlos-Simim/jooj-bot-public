import time

import requests

from main import *
from disnake.ext import commands


class economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="acoes",
                            description="Retorna algumas informações sobre uma determinada ação. Exemplo: TSLA, IBM, NIO, etc.")
    async def acoes(self, ctx, *, acao):
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

    @acoes.error
    async def acoes_error(self, ctx, error):
        print(error)
        await ctx.send("Ação não encontrada.")

    @commands.slash_command(name="moeda", description="Converte uma moeda para outra. Exemplo: 1 dolar para real")
    async def converter_moeda(self, ctx, moeda_origem: str, moeda_destino: str, valor: float):
        await ctx.response.defer()

        try:
            moeda_origem = currency_name_to_code(moeda_origem)
            moeda_destino = currency_name_to_code(moeda_destino)
        except:
            print("Moeda não encontrada.")

        result = get_conversao(moeda_origem, moeda_destino, valor)
        await ctx.send(f"{valor} {moeda_origem} = {round(result * valor, 2)} {moeda_destino}")

    @converter_moeda.error
    async def converter_moeda_error(self, ctx, error):
        print(error)
        await ctx.send(
            "Um erro desconhecido ocorreu. Tente escrever a moeda corretamente, sem plural ou abreviações. Exemplo: Dólar, Real, Bitcoin, etc."
            "\nCaso o erro persista, utilize o código da moeda por enquanto que em breve era será adicionada a lista de traduções. Exemplo: USD, BRL, BTC, etc.")


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


def setup(bot):
    bot.add_cog(economia(bot))
