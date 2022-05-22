import subprocess
import os
import disnake
import json
from typing import List
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()

bot = commands.InteractionBot(
    sync_commands=bool(os.getenv("SYNC_COMMANDS")),
    # test_guilds=[int(os.getenv("DEVELOPER_GUILD_ID"))]
)

faqFile = open("faq.json")
FAQs = json.load(faqFile)


@bot.event
async def on_ready():
    print("{}#{} is ready".format(bot.user.name, bot.user.discriminator))


async def autocomplete_faqs(inter, string: str) -> List[str]:
    return [question for question in FAQs if string.lower() in question.lower()][:10]

# Link to Github to contribute


@bot.slash_command(auto_sync=False, description="Learn how you can contribute to the responses of this bot")
async def contribute(inter: disnake.CommandInteraction):
    return await inter.response.send_message(content="You can contribute by going to https://github.com/Team-Neptune/TeamNeptuneFAQBot", ephemeral=True)


# View FAQ in an ephemeral message (For normal users)

@bot.slash_command(auto_sync=False, description="View answers to Frequently Asked Questions")
async def faq(
    inter: disnake.CommandInteraction,
    question: str = commands.Param(
        autocomplete=autocomplete_faqs, description="Start typing your question to see if it exists")
):
    if question in FAQs.keys():
        faqAnswer = FAQs[question]
        await inter.response.send_message(embed=disnake.Embed(title=question, description=faqAnswer), ephemeral=True)
    else:
        return await inter.response.send_message("Unable to find that FAQ, ask your question in chat so it can be answered and added!", ephemeral=True)


# View FAQ in a public message (For mods users, Manage Messages required)

@bot.slash_command(auto_sync=False, description="View answers to Frequently Asked Questions and post it in chat", default_member_permissions=8192)
async def post_faq(
    inter: disnake.CommandInteraction,
    question: str = commands.Param(
        autocomplete=autocomplete_faqs, description="Start typing the question to see if it exists")
):
    if question in FAQs.keys():
        faqAnswer = FAQs[question]
        await inter.response.send_message(embed=disnake.Embed(title=question, description=faqAnswer))
    else:
        return await inter.response.send_message("Unable to find that FAQ. Once it gets solved, add it!", ephemeral=True)

# Update JSON without bot reload


@bot.slash_command(auto_sync=False, description="Pull latest from Git, update JSON (No bot reload)", default_member_permissions=8)
async def update_faq(
    inter: disnake.CommandInteraction,
):
    await inter.response.defer(ephemeral=True)
    output = subprocess.check_output(["git", "pull"])
    global FAQs
    FAQs = json.load(open("faq.json"))
    return await inter.edit_original_message(content=output)

bot.run(os.getenv("TOKEN"))
