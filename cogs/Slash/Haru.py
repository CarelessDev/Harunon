from discord.user import ClientUser
from discord_slash import SlashContext, cog_ext, SlashCommandOptionType as SOT
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext import commands
import discord
from random import choice
from utils.env import guild_ids, reddit
from utils.data import data
from utils.helix import makeHelix
from datetime import datetime


class Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_emoji(self, emoji_name: str):
        return discord.utils.get(self.bot.emojis, name=emoji_name)

    @cog_ext.cog_slash(
        name="guild", description="Get Guild Metainfo", guild_ids=guild_ids
    )
    async def _guild(self, ctx: SlashContext):
        guilds = self.bot.guilds
        await ctx.send(str(guilds))

    @cog_ext.cog_slash(name="ping", description="Ping Pong 遊ぼう!", guild_ids=guild_ids)
    async def _ping(self, ctx: SlashContext):
        interval = datetime.now() - ctx.created_at
        await ctx.send(
            f"Pong! Ping: {interval.total_seconds() * 1000} ms"
        )

    @cog_ext.cog_slash(
        name="clearmsg", description="Clear All Message", guild_ids=guild_ids,
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
        await ctx.send("Self Destruction: スタート")
        await ctx.channel.purge(limit=int(clear_amount) + 1)

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
        await ctx.send(str(self.get_emoji(emoji_name)))

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
            )
        ]
    )
    async def _haruno(self, ctx: SlashContext, waifu_name: str):
        await ctx.send(choice(data["waifu_gif"][waifu_name]))

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
            )
        ]
    )
    async def _reddit(self, ctx: SlashContext, subreddit: str = "GochiUsa", search_query: str = "chino"):
        msg = await ctx.send("待ってください ちょっとね...")

        try:
            subReddit = await reddit.subreddit(subreddit)
            r = []

            async for i in subReddit.search(search_query, limit=5):
                r.append(i)
            random_sub = choice(r)
            random_sub = await subReddit.random()

            name = random_sub.title
            url = random_sub.url
            ups = random_sub.score
            link = random_sub.permalink
            comments = random_sub.num_comments

            emb = discord.Embed(
                title="はい どうぞ お姉さんに任せていいよ！",
                description=f"```css\n{name}\n```", color=0xf1c40f
            )
            emb.set_author(
                name=ctx.message.author,
                icon_url=ctx.author.avatar_url
            )
            emb.set_footer(
                text=f"Upvote: {ups} Comments: {comments} ・ このハルノには夢がある ❄️"
            )
            emb.set_image(url=url)

            if random_sub.over_18:
                await msg.edit(
                    content="変態 バカ ボケナス 八幡\nhttps://c.tenor.com/qEW8kRsAFV8AAAAC/you-hachiman-oregairu.gif"
                )

            else:
                await msg.edit(
                    content=f"<https://reddit.com{link}> :white_check_mark:", embed=emb
                )

        except Exception as e:
            await msg.edit(content=f"残念ですけど {e}")

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

        await ctx.send("HELIX JIKAN DE~SU!")
        for helix in helixes:
            await ctx.channel.send(helix)

    @cog_ext.cog_slash(
        name="gay", description="Insult someone for being gae", options=[
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
