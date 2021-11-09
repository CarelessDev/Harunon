from discord_slash import  SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext import commands
import discord
import os



class Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))


    @cog_ext.cog_slash(name="test",description="testing jek", guild_ids=[449771987183861760])
    async def _hello(self, ctx:SlashContext):
        guilds = self.bot.guilds
        ids = [guild.id for guild in guilds]
        os.environ['guild_ids'] = str(ids)
        await ctx.send(str(os.environ.get("guild_ids")))

    @cog_ext.cog_slash(name="clear",description="clear message", guild_ids=[449771987183861760])
    async def _clear(self, ctx:SlashContext):
        await ctx.send("comencing self destruct")
        await ctx.channel.purge(limit=3)