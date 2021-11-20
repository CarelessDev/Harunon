from discord.ext import commands
from discord_slash import cog_ext, SlashCommandOptionType as SOT
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from utils.env import guild_ids
from 歌詞.song_lists import song_lists

DISCORD_MSG_LIMIT = 2000


class Kashi(commands.Cog):
    """歌詞"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send("An error occurred: {}".format(str(error)))

    @cog_ext.cog_slash(name="lyric", description="Get Lyric", guild_ids=guild_ids, options=[
        create_option(
            name="song_name",
            description="Name of Song",
            option_type=SOT.STRING,
            required=True,
            choices=[
                create_choice(name=x, value=x) for x in song_lists
            ]
        )
    ])
    async def _kashi(self, ctx: SlashContext, song_name: str):
        file_name = f"./歌詞/{song_name}.haruno"
        with open(file_name, "r") as f:
            lines = self.makeLyrics(f.read(), song_name)
            for l in lines:
                await ctx.send(l)

    @staticmethod
    def makeLyrics(lyrics: str, song_name: str):
        lyrics = lyrics.split("\n")
        lyrics = [x for x in lyrics if x]

        toSend = [song_name]
        currStr = ""

        for l in lyrics:
            currStr += f"{l}\n"
            if len(currStr) > DISCORD_MSG_LIMIT / 2:
                toSend.append(currStr)
                currStr = ""

        if currStr:
            toSend.append(currStr)

        return [f"```\n{line}\n```" for line in toSend]
