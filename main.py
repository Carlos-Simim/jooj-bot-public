from recursos import *


@bot.event  # evento de quando o bot estiver pronto
async def on_ready():
    global dono
    dono = await bot.fetch_user(dono_id)
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name="a"))
    await send_last_commits()
    print(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    await dono.send(f"Bot Reiniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    data_read()


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
bot.run(token)
