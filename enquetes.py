import main
from main import *
from disnake.ext import commands

votacoes_ativas = main.votacoes_ativas


class enquetes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="enquete", description="Cria uma enquete com uma pergunta de sua escolha.")
    async def enquete(self, ctx, *, pergunta=None):
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
                                                           disnake.ui.Button(label="Sim",
                                                                             style=disnake.ButtonStyle.green),
                                                           disnake.ui.Button(label="Não",
                                                                             style=disnake.ButtonStyle.red),
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

        await ctx.response.send_message("Votação criada com sucesso! Não esqueça ela aberta :thumbsup:",
                                        ephemeral=True)

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
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
                        embed.set_footer(
                            text=f"Tempo de votação: {strfdelta(time_var, '{hours}h {minutes}m {seconds}s')}")
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


def setup(bot):
    bot.add_cog(enquetes(bot))
