from random import choice
from discord.ext import commands, tasks
from dotenv import load_dotenv
import discord
import os
import json
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from dotenv import load_dotenv


with open("words.json") as f:
    data = json.load(f)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


bot = commands.Bot(command_prefix=commands.when_mentioned_or('Jek'))
slash = SlashCommand(bot, sync_commands=True)
#slash = SlashCommand(bot, override_type = True)


@bot.event
async def on_ready():
    print('join us')
    change_status.start()


@tasks.loop(seconds=300)
async def change_status():
    status: str = choice(data["activities"])
    activity: discord.Activity = discord.Activity(
        type=discord.ActivityType.listening, name=status)
    await bot.change_presence(activity=activity)


class Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print(self.bot.guilds)

    @slash.slash(name="hello", description="test jek", guild_ids=[449771987183861760])
    async def _hello(ctx: SlashContext):
        await ctx.send("world")


def setup(bot):
    bot.add_cog(Slash(bot))


setup(bot)
bot.run(TOKEN)
