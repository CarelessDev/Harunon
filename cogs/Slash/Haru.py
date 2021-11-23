from discord.user import ClientUser
from discord_slash import SlashContext, cog_ext, SlashCommandOptionType as SOT
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext import commands
import discord
from random import choice
from utils.env import guild_ids, reddit
from utils.data import data
from utils.helix import HelixError, makeHelix
from datetime import datetime
from cogs.Shared.Haru import Haru
import constants.Haruno as Haruno
from utils.slash import SlashUtils


class HaruSlash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="guild", description="Get Guild Metainfo", guild_ids=guild_ids
    )
    async def _guild(self, ctx: SlashContext):
        guilds = self.bot.guilds
        await ctx.send(str(guilds))

    @cog_ext.cog_slash(
        name="ping", description="Ping Pong 遊ぼう!", guild_ids=guild_ids,
        options=[SlashUtils.ephemeral()]
    )
    async def _ping(self, ctx: SlashContext, ephemeral: bool = False):
        interval = datetime.utcnow() - ctx.created_at
        await ctx.send(
            f"Pong! Ping = {interval.total_seconds() * 1000} ms",
            hidden=ephemeral
        )

    @cog_ext.cog_slash(
        name="kamui", description="Clear Messages to delete what you have done", guild_ids=guild_ids,
        options=[
            create_option(
                name="clear_amount",
                description="How many messages to Purge",
                option_type=10,
                required=True
            )
        ]
    )
    async def _cleara(self, ctx: SlashContext, clear_amount: str):
        await ctx.send("**ザ・ハンドが消す!!!**")

        await ctx.channel.purge(limit=int(clear_amount) + 1)

        await ctx.send(f"ザ・ハンドが**{clear_amount}メッセージ**を消した!!!")
        await ctx.channel.send("https://c.tenor.com/xexSk5SQBbAAAAAC/discord-mod.gif")

    @cog_ext.cog_slash(
        name="blep", description="No one have idea what command is this", guild_ids=guild_ids,
        options=[
            create_option(
                name="person",
                description="Who you want to B L E P",
                required=True,
                option_type=6,
            )
        ]
    )
    async def _blep(self, ctx: SlashContext, person: str):
        await ctx.send(str(person.avatar_url))

    @cog_ext.cog_slash(
        name="emoji", description="Send some Emoji!", guild_ids=guild_ids,
        options=[
            create_option(
                name="emoji_name",
                description="Emoji to Echo ACT 3!",
                required=True,
                option_type=SOT.STRING,
            )
        ]
    )
    async def emoji_echo(self, ctx: SlashContext, emoji_name: str):
        await ctx.send(str(Haru.get_emoji(ctx, emoji_name)))

    @cog_ext.cog_slash(
        name="simp", description="SIMP: Super Idol de xiao rong", guild_ids=guild_ids,
        options=[
            create_option(
                name="waifu_name",
                description="Who to SIMP",
                required=True,
                option_type=SOT.STRING,
                choices=[
                    create_choice(value=x, name=x) for x in data["waifu_gif"].keys()
                ]
            ),
            SlashUtils.ephemeral("SIMP without anyone knowing")
        ]
    )
    async def _haruno(self, ctx: SlashContext, waifu_name: str, ephemeral: bool = False):
        await ctx.send(choice(data["waifu_gif"][waifu_name]), hidden=ephemeral)

    @cog_ext.cog_slash(
        name="reddit", description="Reddit!", guild_ids=guild_ids,
        options=[
            create_option(
                name="subreddit",
                description="Subreddit to Grab Photo",
                required=False,
                option_type=SOT.STRING,
            ),
            create_option(
                name="search_query",
                description="Thing to look for",
                required=False,
                option_type=SOT.STRING,
            ),
            SlashUtils.ephemeral("Hide your query to avoid being BONKed")
        ]
    )
    async def _reddit(
        self, ctx: SlashContext,
        subreddit: str = "gochiusa",
        search_query: str = None,
        ephemeral: bool = False
    ):
        if ephemeral:
            await ctx.defer(True)
            msg = None
        else:
            msg = await ctx.send("待ってください ちょっとね...")

        if not search_query:
            if subreddit.lower() == "gochiusa":
                search_query = "chino"

        try:
            subReddit = await reddit.subreddit(subreddit)

            if search_query:
                r = []
                async for i in subReddit.search(search_query, limit=5):
                    r.append(i)
                random_sub = choice(r)
            else:
                random_sub = await subReddit.random()

            name = random_sub.title
            url = random_sub.url
            ups = random_sub.score
            link = random_sub.permalink
            comments = random_sub.num_comments
            r18 = random_sub.over_18

            emb = discord.Embed(
                title="どうぞ お姉さんからよ！" if not r18 else "⚠️⚠️ NSFW ⚠️⚠️",
                description=f"```css\n{name}\n```", color=Haruno.COLOR
            )
            emb.set_author(
                name=ctx.author,
                icon_url=ctx.author.avatar_url
            )
            emb.set_image(url=url)

            if r18 and not ephemeral:
                await msg.edit(
                    content=Haruno.Words.Reddit.R18
                )

            else:
                if r18:
                    emb.set_footer(text="BONK! GO TO HORNY JAIL!")
                else:
                    emb.set_footer(
                        text=f"Upvote: {ups} Comments: {comments}・このハルノには夢がある ❄️"
                    )

                if ephemeral:
                    await ctx.send(
                        content=f"<https://reddit.com{link}> :white_check_mark:",
                        embed=emb,
                        hidden=True,
                    )
                else:
                    await msg.edit(
                        content=f"<https://reddit.com{link}> :white_check_mark:",
                        embed=emb,
                    )

        except Exception as e:
            if ephemeral:
                await ctx.send(content=f"ごめんね {e}", hidden=True)
            else:
                await msg.edit(content=f"ごめんね {e}")

    @cog_ext.cog_slash(
        name="helix", description="Adenine Thymine Cytosine Guanine", guild_ids=guild_ids,
        options=[
            create_option(
                name="text",
                description="Text to Helix-ify",
                required=True,
                option_type=3
            )
        ]
    )
    async def _helix(self, ctx: SlashContext, text: str):
        helixes = makeHelix(text)

        if isinstance(helixes, int):
            if helixes == HelixError.ILLEGAL_CHAR:
                await ctx.send("Illegal String")
            elif helixes == HelixError.TOO_LONG:
                await ctx.send("Someone is trying to break me!")
            else:
                await ctx.send("\"Unknown Error, Blame Nathan\" — Leo")
            return

        await ctx.send("HELIX JIKAN DE~SU!")
        for helix in helixes:
            await ctx.channel.send(helix)

    @cog_ext.cog_slash(
        name="gay", description="Insult someone for being gae", guild_ids=guild_ids,
        options=[
             create_option(
                 name="person",
                 description="Who to insult",
                 required=False,
                 option_type=SOT.USER
             )
        ]
    )
    async def _gay(self, ctx: SlashContext, person: ClientUser = None):
        if person is None:
            await ctx.send(f"<@!{ctx.author_id}> is gay!")

        await ctx.send(f"{person.mention} is gay!")
