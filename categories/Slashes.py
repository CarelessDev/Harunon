from discord_slash import  SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext import commands
import discord, os
from dotenv import load_dotenv

load_dotenv()


guild_ids = [int(id) for id in os.getenv('guild_ids').split(',')]



class Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))


    @cog_ext.cog_slash(name="guild",description="get guild", guild_ids=guild_ids)
    async def _hello(self, ctx:SlashContext):
        guilds = self.bot.guilds
        #ids = [guild.id for guild in guilds]
        await ctx.send(str(guilds))

    @cog_ext.cog_slash(name="clear",description="clear message", guild_ids=guild_ids)
    async def _clear(self, ctx:SlashContext):
        await ctx.send("comencing self destruct")
        await ctx.channel.purge(limit=3)