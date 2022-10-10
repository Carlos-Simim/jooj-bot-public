from main import *


def send_last_commits():
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
