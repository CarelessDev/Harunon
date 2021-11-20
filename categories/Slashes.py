from discord_slash import SlashContext, cog_ext, ComponentContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.utils.manage_components import create_select, create_select_option, create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import json
from random import shuffle


load_dotenv()


guild_ids = [int(id) for id in os.getenv("guild_ids").split(",")]


class Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send("An error occurred: {}".format(str(error)))

    @cog_ext.cog_slash(name="guild", description="Get Guild Metainfo", guild_ids=guild_ids)
    async def _guild(self, ctx: SlashContext):
        guilds = self.bot.guilds
        await ctx.send(str(guilds))

    @cog_ext.cog_slash(name="ase", description="african s energy", guild_ids=guild_ids,
                       options=[create_option(name="option",
                                              description="nigga",
                                              required=True,
                                              option_type=3,
                                              choices=[create_choice(name="yes", value="ชังชาติ"),
                                                       create_choice(name="no", value="nigga")]
                                              )])
    async def _ase(self, ctx: SlashContext, option: str):
        await ctx.send(option)

    @cog_ext.cog_slash(name="clearmsg", description="Clear All Message", guild_ids=guild_ids,
                       options=[create_option(name="clear_amount",
                                              description="How many messages to Purge",
                                              option_type=10,
                                              required=True)])
    async def _cleara(self, ctx: SlashContext, clear_amount: str):
        await ctx.send("comencing self destruct")
        await ctx.channel.purge(limit=int(clear_amount) + 1)

    @cog_ext.cog_slash(name="blep", description="Wtf command is this", guild_ids=guild_ids,
                       options=[create_option(name="person",
                                              description="Who you want to B L E P",
                                              required=True,
                                              option_type=6,
                                              )])
    async def _blep(self, ctx: SlashContext, person: str):
        # print(dir(person))
        await ctx.send(str(person.avatar_url))

   