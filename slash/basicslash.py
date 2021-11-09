import discord,os 
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="Jek")
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print(bot.guilds)
    


@slash.slash(name="test",description="test jek", guild_ids=[449771987183861760])
async def _test(ctx:SlashContext):
    await ctx.send("Test")


bot.run(TOKEN)