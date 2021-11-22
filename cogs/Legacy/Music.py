import discord
from discord.ext import commands
import asyncio
import asyncio
import math
import constants.Haruno as Haruno
from cogs.Shared.Music import Song, Song_queue
from cogs.Shared.Music import Song, YTDLSource, VoiceError


class MusicLegacy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop = None
        self.song = {}

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send("An error occurred: {}".format(str(error)))

    async def play_nexts_song(self, ctx):
        global Song_queue
        player = ctx.voice_client
        server_id = ctx.voice_client.server_id if ctx else None
        if self.loop[server_id]:
            source = await YTDLSource.create_source(ctx, self.song[server_id].url)
            Song_queue[server_id].append(source)
        if (Song_queue[server_id] != [] and server_id):
            self.song[server_id] = Song_queue[server_id].pop(0)
            #print([x.title for x in Song_queue[server_id]])
            player.play(self.song[server_id], after=lambda x=None: asyncio.run(
                self.play_nexts_song(ctx)))
        else:
            return

    @commands.command(name="join", aliases=["j"])
    async def _join(self, ctx: commands.context, *, channel: discord.VoiceChannel = None):
        """Join user VC"""
        if not channel and not ctx.author.voice:
            raise VoiceError(
                "You are neither connected to a voice channel nor specified a channel to join."
            )

        destination = channel or ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(destination)
            return
        else:
            await destination.connect()
            await ctx.send(Haruno.Words.JOIN)

    @commands.command(name="leave", aliases=["le"])
    async def _leave(self, ctx: commands.context):
        """leave vc"""
        await ctx.voice_client.disconnect()
        await ctx.send(Haruno.Words.LEAVE)

    @commands.command(name="skip", aliases=["s"])
    async def _skip(self, ctx: commands.context):
        """skip current song"""
        if not ctx.voice_client.is_playing:
            return await ctx.send(Haruno.Words.Skip.NOT_PLAYING)
        # Song_queue[ctx.voice_client.server_id].pop(0)
        ctx.voice_client.stop()
        msg = await ctx.send(Haruno.Words.Skip.SUCCESS)
        await msg.add_reaction(Haruno.Emoji.SKIP)

    @commands.command(name="pause", aliases=["pa"])
    async def _pause(self, ctx: commands.context):
        """pause current song"""
        if not ctx.voice_client.is_playing:
            return await ctx.send(Haruno.Words.Pause.NOT_PLAYING)
        if ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            ctx.voice_client.pause()
            await ctx.message.add_reaction(Haruno.Emoji.PAUSE_RESUME)

    @commands.command(name="resume", aliases=["res"])
    async def _resume(self, ctx: commands.context):
        """resume"""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.message.add_reaction(Haruno.Emoji.PAUSE_RESUME)

    @commands.command(name="queue", aliases=["q"])
    async def _queue(self, ctx: commands.context, page: int = 1):
        """Display list of songs"""
        global Song_queue

        server_id = ctx.message.guild.id
        if not Song_queue[server_id] and not ctx.voice_client.is_playing():
            return await ctx.send(Haruno.Words.Queue.EMPTY)
        page = page
        items_per_page = 10
        pages = math.ceil((len(Song_queue[server_id]) + 1) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ""
        for i, song in enumerate([ctx.voice_client.source] + Song_queue[server_id][start:end], start=start):
            queue += "`{0}.` [**{1.title}**]({1.url}){2}\n".format(
                i + 1, song,
                " <<< Now Playing" if i == 0 else ""
            )

        embed = (
            discord.Embed(
                description=f"**{len(Song_queue[server_id])} Songs in Queue:**\n\n{queue}", color=Haruno.COLOR
            )
            .set_footer(text=f"Viewing page {page}/{pages}"))

        await ctx.send(embed=embed)

    @commands.command(name="loop", aliases=["l"])
    async def _loop_queue(self, ctx: commands.context):
        """loop queue"""
        server_id = ctx.message.guild.id
        self.loop = self.loop if self.loop else {guild_id: loop for (
            guild_id, loop) in [(i.id, False) for i in self.bot.guilds]}
        if self.loop[server_id] == False:
            self.loop[server_id] = True
            msg = await ctx.send(Haruno.Words.Loop.ON)
            await msg.add_reaction(Haruno.Emoji.Loop.ON)
        else:
            self.loop[server_id] = False
            msg = await ctx.send(Haruno.Words.Loop.OFF)
            await msg.add_reaction(Haruno.Emoji.Loop.OFF)

    @commands.command(name="play", aliases=["p", "lay"])
    async def _play(self, ctx: commands.context, *, song: str):
        """play song, search or url"""
        global Song_queue
        async with ctx.typing():

            await ctx.invoke(self._join)

            server_id = ctx.voice_client.server_id
            self.loop = self.loop if self.loop else {guild_id: loop for (
                guild_id, loop) in [(i.id, False) for i in self.bot.guilds]}

            source = await YTDLSource.create_source(ctx, song, loop=self.bot.loop)
            if server_id in Song_queue:
                Song_queue[server_id].append(source)
            else:
                Song_queue[server_id] = [source]
            if not ctx.voice_client.is_playing():
                self.song[server_id] = Song_queue[server_id].pop(0)
                ctx.voice_client.play(self.song[server_id], after=lambda e: asyncio.run(
                    self.play_nexts_song(ctx)))
            song = Song(source)
        await ctx.send(embed=song.create_embed(ctx.message.created_at, Haruno.Words.ENQUEUED))

    @commands.command(name="remove", aliases=["rm"])
    async def _remove(self, ctx: commands.context, index: int = 1):
        global Song_queue
        if not ctx.author.voice:
            return await ctx.send("no")
        server_id = ctx.message.guild.id
        if Song_queue[server_id] != []:
            index = min(max(index, -1), len(Song_queue[server_id]))

            if not self.loop[server_id]:
                ctx.voice_client.stop()
            msg = await ctx.send("Removed {1} [**{0.title}**](<{0.url}>) 成功!".format(Song_queue[server_id].pop(index - 1), index))
            await msg.add_reaction("✅")
        else:
            return await ctx.send(Haruno.Words.Queue.EMPTY)

    @commands.command(name="now", aliases=["n"])
    async def _now(self, ctx: commands.Context):
        """show current song"""
        await ctx.send(embed=Song(ctx.voice_client.source).create_embed(ctx.message.created_at))

    @commands.command(name="clear", aliases=["c"])
    async def _clear(self, ctx: commands.Context):
        """clear queue"""
        global Song_queue
        server_id = ctx.voice_client.server_id
        Song_queue[server_id] = []
        msg = await ctx.send(Haruno.Words.Queue.CLEARED)
        await msg.add_reaction("✅")
