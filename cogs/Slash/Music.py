from discord_slash import SlashContext, cog_ext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_actionrow, create_button, create_select_option, wait_for_component, create_select
from discord_slash.model import ButtonStyle
import discord
from discord.ext import commands
import asyncio
import math
from utils.env import guild_ids
from cogs.Shared.Music import Song_queue
import constants.Haruno as Haruno
from cogs.Shared.Music import Song, YTDLSource, VoiceError
from youtube_search import YoutubeSearch


class MusicSlash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop = None
        self.song = {}

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

    @cog_ext.cog_slash(
        name="join", description="Join Voice Chat", guild_ids=guild_ids, options=[
            create_option(
                name="channel", description="Voice Channel to join", required=False, option_type=3
            )
        ]
    )
    async def _join(self, ctx: SlashContext, *, channel: str = None):
        destination = channel or ctx.author.voice.channel
        if ctx.voice_client:
            return await ctx.voice_client.move_to(destination)
        else:
            return await destination.connect()

    @cog_ext.cog_slash(name="leave", description="Leave Voice Chat", guild_ids=guild_ids)
    async def _leave(self, ctx: SlashContext):
        await ctx.voice_client.disconnect()
        await ctx.send(Haruno.Words.LEAVE)

    @cog_ext.cog_slash(name="skip", description="Skip a Song", guild_ids=guild_ids)
    async def _skip(self, ctx: SlashContext):
        if not ctx.voice_client.is_playing:
            return await ctx.send(Haruno.Words.Skip.NOT_PLAYING)
        ctx.voice_client.stop()
        msg = await ctx.send(Haruno.Words.Skip.SUCCESS)
        await msg.add_reaction(Haruno.Emoji.SKIP)

    @cog_ext.cog_slash(name="pause", description="Pause the Song", guild_ids=guild_ids)
    async def _pause(self, ctx: SlashContext):
        if not ctx.voice_client.is_playing:
            return await ctx.send(Haruno.Words.Pause.NOT_PLAYING)
        if ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            ctx.voice_client.pause()
            msg = await ctx.send(Haruno.Words.Pause.SUCCESS)
            await msg.add_reaction(Haruno.Emoji.PAUSE_RESUME)

    @cog_ext.cog_slash(name="resume", description="Resume the Song", guild_ids=guild_ids)
    async def _resume(self, ctx: SlashContext):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            msg = await ctx.send(Haruno.Words.Resume.SUCCESS)
            await msg.add_reaction(Haruno.Emoji.PAUSE_RESUME)

    @cog_ext.cog_slash(name="queue", description="Show the Queue", guild_ids=guild_ids)
    async def _queue(self, ctx: SlashContext):
        global Song_queue
        server_id = ctx.guild_id

        if not Song_queue[server_id] and not ctx.voice_client.is_playing():
            return await ctx.send(Haruno.Words.Queue.EMPTY)

        buttons = [
            create_button(
                style=ButtonStyle.green,
                label="Prev",
                custom_id="p"
            ),
            create_button(
                style=ButtonStyle.red,
                label="Next",
                custom_id="n"
            ),
        ]
        action_row = create_actionrow(*buttons)
        page = 1
        items_per_page = 2
        pages = math.ceil((len(Song_queue[server_id]) + 1) / items_per_page)
        once = True

        while True:
            server_id = ctx.guild_id
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
                    description=f"**{len(Song_queue[server_id]) + 1} Songs in Queue:**\n\n{queue}", color=Haruno.COLOR
                )
                .set_footer(text=f"Viewing page {page}/{pages}"))

            if once:
                await ctx.send(embed=embed, components=[action_row])
                once = False
            else:
                await button_ctx.edit_origin(embed=embed)

            button_ctx: ComponentContext = await wait_for_component(self.bot, components=[action_row])

            if button_ctx.component_id == 'p':
                page = page - 1 if page != 1 else 1
            elif button_ctx.component_id == 'n':
                page = page + 1 if page != pages else pages

    @cog_ext.cog_slash(name="loop", description="Loop!", guild_ids=guild_ids)
    async def _loop_queue(self, ctx: SlashContext):
        server_id = ctx.guild_id
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

    @cog_ext.cog_slash(
        name="play", description="Play some Music", guild_ids=guild_ids,
        options=[
            create_option(
                name="song",
                description="Song Name",
                required=True,
                option_type=3
            )
        ]
    )
    async def _play(self, ctx: SlashContext,  song: str):
        global Song_queue

        await ctx.invoke(self._join)

        server_id = ctx.voice_client.server_id
        self.loop = self.loop if self.loop else {guild_id: loop for (
            guild_id, loop) in [(i.id, False) for i in self.bot.guilds]}

        await ctx.defer()
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
        await ctx.send(embed=song.create_embed(ctx.created_at, Haruno.Words.ENQUEUED))

    @cog_ext.cog_slash(
        name="search", description="Search for Music", guild_ids=guild_ids,
        options=[
            create_option(
                name="song",
                description="Search Query",
                required=True,
                option_type=3
            )
        ]
    )
    async def _search(self, ctx: SlashContext,  song: str):
        await ctx.defer()

        results = YoutubeSearch(song, max_results=10).to_dict()
        text = ""
        for i, song in enumerate(results):
            text += f"`{i + 1}.` [**{song['title']} - {song['channel']} ({song['duration']})**](https://www.youtube.com/{song['url_suffix']})\n"

        embed = discord.Embed(
            description=f"**{len(results)} Results:**\n\n{text}", color=Haruno.COLOR
        ).set_footer(text="このハルノには夢がある ❄️")
        select = create_select(
            options=[
                create_select_option(
                    f"{song['title']} - {song['channel']}", value=song['url_suffix'], emoji="❄️"
                ) for song in results],
            placeholder="song",
            min_values=1,
            max_values=1,
        )

        msg = await ctx.send(embed=embed, components=[create_actionrow(select)])

        button_ctx: ComponentContext = await wait_for_component(self.bot, components=[select])
        url = f"https://www.youtube.com{button_ctx.selected_options[0]}"
        await ctx.invoke(self._play, song=url)

    @cog_ext.cog_slash(
        name="remove", description="Remove Song from Queue", guild_ids=guild_ids,
        options=[
            create_option(
                name="index",
                description="Song Index to remove",
                required=True,
                option_type=10
            )
        ]
    )
    async def _remove(self, ctx: SlashContext, index: int):
        global Song_queue
        if not ctx.author.voice:
            return await ctx.send("no")
        server_id = ctx.guild_id
        if Song_queue[server_id] != []:
            index = min(max(index, -1), len(Song_queue[server_id]))

            if not self.loop[server_id]:
                ctx.voice_client.stop()
            msg = await ctx.send("Removed {1} [**{0.title}**](<{0.url}>) 成功!".format(Song_queue[server_id].pop(index - 1), index))
            await msg.add_reaction("✅")
        else:
            return await ctx.send(Haruno.Words.Queue.EMPTY)

    @cog_ext.cog_slash(name="now", description="Show Current Song", guild_ids=guild_ids)
    async def _now(self, ctx: commands.Context):
        await ctx.send(embed=Song(ctx.voice_client.source).create_embed(ctx.created_at))

    @cog_ext.cog_slash(name="clear", description="Clear the Queue", guild_ids=guild_ids)
    async def _clear(self, ctx: commands.Context):
        server_id = ctx.voice_client.server_id
        Song_queue[server_id] = []
        self.song[server_id] = None
        msg = await ctx.send(Haruno.Words.Queue.CLEARED)
        await msg.add_reaction("✅")
