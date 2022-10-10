from main import *
from disnake.ext import commands

test_guild = [1007317177520619610]


class lol(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="elos",
                            description="Retorna o ELO + Divisão + Campeão de todos os jogadores de uma partida ativa.")
    async def elos(self, ctx, *, nick: str):
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
    async def elos_error(self, ctx, error):
        await ctx.send(f'Não foi possível encontrar a partida de ``{ctx.options["nick"]}``')
        await dono.send(error)

    @commands.slash_command(name="perfil",
                            description="Retorna algumas informações do perfil da pessoa e da última partida jogada.")
    async def perfil(self, ctx, *, nick: str):
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
            url="https://opgg-static.akamaized.net/images/profile_icons/profileIcon" + str(
                me['profileIconId']) + ".jpg")

        await ctx.send(embed=embedVar)

    @perfil.error
    async def perfil_error(self, ctx, error):
        await ctx.send(
            "Erro inesperado ao buscar informações do jogador. Verifique se o nick está correto e tente novamente, tente novamente mais tarde caso o problema persista.")
        await dono.send(
            f"Erro inesperado ao buscar informações de algum jogador, verifique os logs do bot. Erro: {error}")


def get_matches_info(nick):
    me = getSummonerByName(nick)
    league_info = watcher.league.by_summoner(my_region, me['id'])
    my_matches = watcher.match.matchlist_by_puuid(my_region, me['puuid'])
    last_match = watcher.match.by_id(my_region, my_matches[0])
    return me, league_info, last_match


def get_live_match(nick):
    me = getSummonerByName(nick)
    return watcher.spectator.by_summoner(region=my_region, encrypted_summoner_id=me['id'])


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
    runas_dicionario: dict = {"Dark Harvest": "Colheita Sombria", "Electrocute": "Eletrocutar",
                              "Predator": "Predador",
                              "Hail of Blades": "Chuva de Lâminas", "Summon Aery": "Aery", "Arcane Comet": "Cometa",
                              "Phase Rush": "Ímpeto", "Lethal Tempo": "Ritmo Fatal",
                              "Grasp of the Undying": "Grasp",
                              "Aftershock": "Pós-Choque", "Glacial Augment": "Gelinho",
                              "Unsealed Spellbook": "Livro"}

    for rune_tree in response.json():
        for rune_var in rune_tree['slots']:
            for runes in rune_var['runes']:
                if runes['id'] == rune_name:
                    return runas_dicionario.get(runes['name'])

    return "Runa não encontrada"


def getSummonerByName(name):
    return watcher.summoner.by_name(my_region, name)


def setup(bot):
    bot.add_cog(lol(bot))
