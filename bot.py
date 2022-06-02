import random
import subprocess
import os
from this import d
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
    print(f"{bot.user.name}#{bot.user.discriminator} is ready\nGuild count: {len(bot.guilds)}")


def searchFAQs(searchTerm: str, ignoreExactMatches: bool = False) -> List[str]:
    if len(searchTerm.strip()) == 0:
        return [question for question in FAQs][:10]
    searchTermElements = searchTerm.split()
    # TEST:0
    results = {}

    def get_question_points(question):
        return results[question]
    for ste in searchTermElements:
        for q in FAQs:
            if searchTerm.lower() == q.lower() and not ignoreExactMatches:
                return [q]
            if ste.lower() in q.lower():
                if q in results:
                    results[q] = results[q] + 1
                else:
                    results[q] = 1
    resultQuestions = [question for question in results]
    resultQuestions.sort(key=get_question_points, reverse=True)
    return resultQuestions


async def autocomplete_faqs(inter, searchTerm: str) -> List[str]:
    return searchFAQs(searchTerm=searchTerm)[:10]


def generateRandomFAQs(overrideList: list = None, baseOnTerm: str = None) -> List[str]:
    basedOnList = overrideList or FAQs.keys()
    if baseOnTerm:
        results = searchFAQs(baseOnTerm, ignoreExactMatches=True)
        otherFaqOne = results[1]
        otherFaqTwo = results[2] or None
        otherFaqThree = results[3] or None
    else:
        randomNumber = random.randrange(len(basedOnList))
        if (len(basedOnList) - randomNumber) <= 5:
            randomNumber = randomNumber-5
        otherFaqOne = list(basedOnList)[randomNumber]
        otherFaqTwo = list(basedOnList)[randomNumber+1] or None
        otherFaqThree = list(basedOnList)[randomNumber+2] or None
    return [otherFaqOne, otherFaqTwo, otherFaqThree]

# Link to Github to contribute


@bot.slash_command(auto_sync=bool(os.getenv("SYNC_COMMANDS")), description="Learn how you can contribute to the responses of this bot")
async def contribute(inter: disnake.CommandInteraction):
    return await inter.response.send_message(content="You can contribute by going to https://github.com/Team-Neptune/TeamNeptuneFAQBot", ephemeral=True)


# View FAQ in an ephemeral message (For normal users)

@bot.slash_command(auto_sync=bool(os.getenv("SYNC_COMMANDS")), description="View answers to Frequently Asked Questions")
async def faq(
    inter: disnake.CommandInteraction,
    question: str = commands.Param(
        autocomplete=autocomplete_faqs, description="Start typing your question to see if it exists")
):
    if question in FAQs.keys():
        faqAnswer = FAQs[question]
        randomlyGenerated = generateRandomFAQs(baseOnTerm=question)

        class OtherFaqsDropdown(disnake.ui.Select):
            def __init__(self):
                options = [
                    disnake.SelectOption(
                        label=question, description=FAQs[question][0:100], value=str(
                            question), emoji="⭐"
                    )
                ]
                for otherFaq in randomlyGenerated:
                    if otherFaq is not None:
                        options.append(disnake.SelectOption(
                            label=otherFaq, description=FAQs[otherFaq][0:100], value=str(
                                otherFaq)
                        ))
                super().__init__(
                    placeholder="Related FAQs",
                    min_values=1,
                    max_values=1,
                    options=options,
                )

            async def callback(self, interaction: disnake.MessageInteraction):
                requestedQuestion = self.values[0]
                await interaction.response.edit_message(embed=disnake.Embed(title=requestedQuestion, description=FAQs[requestedQuestion]), view=OtherFAQsView())

        class OtherFAQsView(disnake.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(OtherFaqsDropdown())

        await inter.response.send_message(embed=disnake.Embed(title=question, description=faqAnswer), ephemeral=True, view=OtherFAQsView())
    else:
        return await inter.response.send_message("Unable to find that FAQ, ask your question in chat so it can be answered and added!", ephemeral=True)


# View FAQ in a public message (For mods users, Manage Messages required)

@bot.slash_command(auto_sync=bool(os.getenv("SYNC_COMMANDS")), description="View answers to Frequently Asked Questions and post it in chat", default_member_permissions=8192)
async def post_faq(
    inter: disnake.CommandInteraction,
    question: str = commands.Param(
        autocomplete=autocomplete_faqs, description="Start typing the question to see if it exists")
):
    if question in FAQs.keys():
        faqAnswer = FAQs[question]
        await inter.response.send_message(embed=disnake.Embed(title=question, description=faqAnswer).set_footer(text="ℹ️ Search for answers yourself by using the /faq command!"))
    else:
        return await inter.response.send_message("Unable to find that FAQ. Once it gets solved, add it!", ephemeral=True)

# Update JSON without bot reload


@bot.slash_command(auto_sync=bool(os.getenv("SYNC_COMMANDS")), description="Pull latest from Git, update JSON (No bot reload)", default_member_permissions=8)
async def update_faq(
    inter: disnake.CommandInteraction,
):
    await inter.response.defer(ephemeral=True)
    output = subprocess.check_output(["git", "pull"])
    global FAQs
    FAQs = json.load(open("faq.json"))
    return await inter.edit_original_message(content=output)

bot.run(os.getenv("TOKEN"))
