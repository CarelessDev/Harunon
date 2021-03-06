from discord.ext import commands
from datetime import datetime
from utils.env import reddit
import discord
from random import choice
import constants.Haruno as Haruno


class HaruLegacy(commands.Cog):
    """陽乃ベストお姉さん"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send("An error occurred: {}".format(str(error)))

    @commands.command(name="ping")
    async def _ping(self, ctx: commands.Context):
        """Ping Pong 遊ぼう!"""
        interval = datetime.utcnow() - ctx.message.created_at
        await ctx.send(
            f"Pong! Ping = {interval.total_seconds() * 1000} ms"
        )

    @commands.command(name="reddit", aliases=["r",  "r/"])
    async def reddit(self, ctx, *, req: str = None):
        """use simpr <subreddit> <search>"""
        msg = await ctx.send("Loading ... ")

        if req:
            search = req.split()
            subreddit = await reddit.subreddit(search[0])
            if len(search) > 1:
                r = []
                async for i in subreddit.search(str(search[1:]), limit=5):
                    r.append(i)
                random_sub = choice(r)
            else:
                random_sub = await subreddit.random()
        else:
            subreddit = await reddit.subreddit("GochiUsa")
            random_sub = await subreddit.random()

        name = random_sub.title
        url = random_sub.url
        ups = random_sub.score
        link = random_sub.permalink
        comments = random_sub.num_comments

        emb = discord.Embed(
            title="here some sauce",
            description=f"```css\n{name}\n```", color=Haruno.COLOR
        )
        emb.set_author(name=ctx.message.author, icon_url=ctx.author.avatar_url)

        if random_sub.over_18:
            emb.set_footer(text="18+ huh You disgusting fuck")

            await msg.edit(content=f"<https://reddit.com{link}>", embed=emb)
            await ctx.channel.send(f"|| {url} ||")

        else:
            await msg.edit(content=f"<https://reddit.com{link}> :white_check_mark:")
            emb.set_footer(text="Here is your meme!")
            emb.set_image(url=url)
            await ctx.send(embed=emb)
