import random
import subprocess
import os
from this import d
import disnake
from disnake import ButtonStyle
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


async def autocomplete_faqs(inter, searchTerm: str) -> List[str]:
    if len(searchTerm.strip()) == 0:
        return [question for question in FAQs][:10]
    searchTermElements = searchTerm.split()
    results = []
    for s in searchTermElements:
        for q in FAQs:
            if searchTerm.lower() == q.lower():
                return [q]
            if s.lower() in q.lower():
                if q not in results:
                    results.append(q)
    return results[:10]


def generateRandomFAQs() -> List[str]:
    randomNumber = random.randrange(len(FAQs.keys()))
    if (len(FAQs.keys()) - randomNumber) <= 3:
        randomNumber = randomNumber-3
    otherFaqOne = list(FAQs.keys())[randomNumber]
    otherFaqTwo = list(FAQs.keys())[randomNumber+1]
    otherFaqThree = list(FAQs.keys())[randomNumber+2]
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
        randomlyGenerated = generateRandomFAQs()
        otherFaqOne = randomlyGenerated[0]
        otherFaqTwo = randomlyGenerated[1]
        otherFaqThree = randomlyGenerated[2]

        class OtherFaqsDropdown(disnake.ui.Select):
            def __init__(self):
                options = [
                    disnake.SelectOption(
                        label=otherFaqOne, description=FAQs[otherFaqOne][0:100], value=str(
                            otherFaqOne)
                    ),
                    disnake.SelectOption(
                        label=otherFaqTwo, description=FAQs[otherFaqTwo][0:100], value=str(
                            otherFaqTwo)
                    ),
                    disnake.SelectOption(
                        label=otherFaqThree, description=FAQs[otherFaqThree][0:100], value=str(
                            otherFaqThree)
                    ),
                ]
                super().__init__(
                    placeholder="Other FAQs you may need",
                    min_values=1,
                    max_values=1,
                    options=options,
                )

            async def callback(self, interaction: disnake.MessageInteraction):
                requestedQuestion = self.values[0]
                randomlyGenerated = generateRandomFAQs()
                otherFaqOne = randomlyGenerated[0]
                otherFaqTwo = randomlyGenerated[1]
                otherFaqThree = randomlyGenerated[2]

                class OtherFaqsDropdownResponded(disnake.ui.Select):
                    def __init__(self):
                        options = [
                            disnake.SelectOption(
                                label=otherFaqOne, description=FAQs[otherFaqOne][0:100], value=str(
                                    otherFaqOne)
                            ),
                            disnake.SelectOption(
                                label=otherFaqTwo, description=FAQs[otherFaqTwo][0:100], value=str(
                                    otherFaqTwo)
                            ),
                            disnake.SelectOption(
                                label=otherFaqThree, description=FAQs[otherFaqThree][0:100], value=str(
                                    otherFaqThree)
                            ),
                        ]
                        super().__init__(
                            placeholder="Other FAQs you may need",
                            min_values=1,
                            max_values=1,
                            options=options,
                        )

                    async def callback(self, interaction: disnake.MessageInteraction):
                        requestedQuestion = self.values[0]
                        await interaction.response.edit_message(embed=disnake.Embed(title=requestedQuestion, description=FAQs[requestedQuestion]), view=OtherFAQsView())

                class OtherFAQsViewResponded(disnake.ui.View):
                    def __init__(self):
                        super().__init__()
                        self.add_item(OtherFaqsDropdownResponded())
                await interaction.response.edit_message(embed=disnake.Embed(title=requestedQuestion, description=FAQs[requestedQuestion]), view=OtherFAQsViewResponded())

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
        await inter.response.send_message(embed=disnake.Embed(title=question, description=faqAnswer))
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
