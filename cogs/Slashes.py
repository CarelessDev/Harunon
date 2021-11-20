from discord_slash import SlashContext, cog_ext
import discord_slash
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
import discord
from random import choice
from utils.env import guild_ids
from utils.data import data


class Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_emoji(self, emoji_name: str):
        return discord.utils.get(self.bot.emojis, name=emoji_name)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send("An error occurred: {}".format(str(error)))

    @cog_ext.cog_slash(name="guild", description="Get Guild Metainfo", guild_ids=guild_ids)
    async def _guild(self, ctx: SlashContext):
        guilds = self.bot.guilds
        await ctx.send(str(guilds))

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
        await ctx.send(str(person.avatar_url))

    @cog_ext.cog_slash(name="emoji", description="Send some Emoji!", guild_ids=guild_ids,
                       options=[
                           create_option(
                               name="emoji_name",
                               description="Emoji to Echo ACT 3!",
                               required=True,
                               option_type=discord_slash.SlashCommandOptionType.STRING,
                           )
                       ])
    async def emoji_echo(self, ctx: SlashContext, emoji_name: str):
        await ctx.send(str(self.get_emoji(emoji_name)))

    @cog_ext.cog_slash(name="haruno", description="雪ノ下陽乃", guild_ids=guild_ids)
    async def _haruno(self, ctx: SlashContext):
        await ctx.send(choice(data["haruno_gif"]))
