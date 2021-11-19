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

    # @cog_ext.cog_slash(name="questchi", description="how well do u know chi", guild_ids=guild_ids,
    #                    options=[create_option(name="start",
    #                                           description="this chi is made for chi to test himself",
    #                                           required=True,
    #                                           option_type=3,
    #                                           choices=[create_choice(name="starto", value="1"),
    #                                                    create_choice(name="next time", value="0")])])
    # async def _ase(self, ctx: SlashContext, start: str):
    #     # await ctx.send(bool(int(start)))

    #     if not bool(int(start)):
    #         embed = discord.Embed(
    #             title="imagine won't even try to answer chi questions", color=0x66ff99)
    #         embed.add_field(name="Loser", value=ctx.author.mention)
    #         embed.set_author(name=ctx.author.name,
    #                          icon_url=ctx.author.avatar_url)
    #         await ctx.send(embed=embed)
    #     else:
    #         with open("./words.json", "r") as q:
    #             questions = json.load(q)["questchi"]
    #             shuffle(questions)
    #         buttons = [create_button(
    #             style=ButtonStyle.green,
    #             label="quit",
    #             custom_id="q"),
    #             create_button(
    #             style=ButtonStyle.red,
    #             label="skip",
    #             custom_id="s")
    #         ]
    #         action_row = create_actionrow(*buttons)
    #         score = 0
    #         amount = 0
    #         for question, answers in questions:
    #             amount += 1
    #             shuffle(answers)
    #             select = create_select(
    #                 options=[  # the options in your dropdown
    #                     create_select_option(ans[:-1], value=ans[-1], emoji="🥼") for ans in answers],
    #                 # the placeholder text to show when no options have been chosen
    #                 placeholder="Choose your answer",
    #                 min_values=1,  # the minimum number of options a user must select
    #                 max_values=1,  # the maximum number of options a user can select
    #             )
    #             embed = discord.Embed(title=question, color=0x66ff99)
    #             # like action row with buttons but without * in front of the variable
    #             await ctx.send(embed=embed, components=[create_actionrow(select), action_row])

    #             for i in range(2):
    #                 button_ctx: ComponentContext = await wait_for_component(self.bot, components=[select, action_row])

    #                 # await button_ctx.edit_origin(content="You pressed a button!")
    #                 # await button_ctx.send(str(button_ctx.selected_options))
    #                 # print(dir(button_ctx))
    #                 if not button_ctx.selected_options:
    #                     if button_ctx.component_id == "q":
    #                         break
    #                     elif button_ctx.component_id == "s":
    #                         embed = discord.Embed(
    #                             title="smh imagine skipping", color=0x66ff99)
    #                         embed.set_author(
    #                             name=button_ctx.author.name, icon_url=button_ctx.author.avatar_url)
    #                         await button_ctx.send(embed=embed)
    #                         break

    #                 elif list(button_ctx.selected_options) == ["1"]:
    #                     answered = [
    #                         x for x in button_ctx.component["options"] if x["value"] == "1"][0]["label"]

    #                     embed = discord.Embed(
    #                         title=f"{button_ctx.author.nick} is right!!!, the answer is {answered}", color=0x66ff99)
    #                     embed.set_author(
    #                         name=button_ctx.author.name, icon_url=button_ctx.author.avatar_url)
    #                     await button_ctx.send(embed=embed)
    #                     score += 1
    #                     break
    #                 else:
    #                     answered = [x for x in button_ctx.component["options"] if list(
    #                         x["value"]) == button_ctx.selected_options][0]["label"]
    #                     # print(button_ctx.selected_options)
    #                     if i < 1:
    #                         embed = discord.Embed(
    #                             title=f"Ha {button_ctx.author.nick} suck!, it is not {answered} try again", color=0xff6666)
    #                         embed.set_author(
    #                             name=button_ctx.author.name, icon_url=button_ctx.author.avatar_url)
    #                         await button_ctx.send(embed=embed)
    #                     else:
    #                         embed = discord.Embed(
    #                             title=f"What a foking idiot {button_ctx.author.nick},it is also not {answered} u cant even get it right the second time{'.' if amount == len(questions) else ', anyway next.'}", color=0xf1c40f)
    #                         embed.set_author(
    #                             name=button_ctx.author.name, icon_url=button_ctx.author.avatar_url)
    #                         await button_ctx.send(embed=embed)
    #             if button_ctx.component_id == "q":
    #                 break
    #         embed = discord.Embed(
    #             title=f"welp that the end, the score: {score}/{amount}", color=0x66ff99)
    #         await ctx.send(embed=embed)
