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
    async def _guild(self, ctx:SlashContext):
        guilds = self.bot.guilds
        #ids = [guild.id for guild in guilds]
        await ctx.send(str(guilds))

    @cog_ext.cog_slash(name="clear",description="clear message", guild_ids=guild_ids)
    async def _clear(self, ctx:SlashContext):
        await ctx.send("comencing self destruct")
        await ctx.channel.purge(limit=3)


    @cog_ext.cog_slash(name="ASE",description="african s energy", guild_ids=guild_ids,
            options=[create_option(name='option',
                                    description='nigga',
                                    required=True,
                                    option_type=3,
                                    choices=[create_choice(name="yes",value="ชังชาติ"),
                                             create_choice(name="no", value="nigga")]
                                             )])
    async def _ase(self, ctx:SlashContext, option:str):
        await ctx.send(option)

    @cog_ext.cog_slash(name="test",description="testing", guild_ids=guild_ids,
            options=[create_option(name='hi',
                                    description='num',
                                    option_type=10,
                                    required=False)])

    async def _test(self, ctx:SlashContext, option:str):
        print()
        #await ctx.send(option)