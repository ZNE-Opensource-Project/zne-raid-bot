import asyncio
import random
import aiohttp
import discord

from core.utils.helpers import send_message_http


def multiplespam_panel(messages: list[str]):
    display = "\n".join(f"```{m}```" for m in messages)

    class MultipleSpamPanel(discord.ui.LayoutView):
        def __init__(self):
            super().__init__(timeout=None)
            self.messages = messages

        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"# PRESS BUTTON TO START SPAM!\n-# you are spamming the following messages randomly:\n{display}"),
            discord.ui.ActionRow(
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="SPAM 5X",
                    custom_id="multi_spam_5x",
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="SPAM 10X",
                    custom_id="multi_spam_10x",
                ),
            ),
            accent_colour=discord.Colour(16777215),
        )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            cid = interaction.data.get("custom_id")

            if cid == "multi_spam_5x":
                await interaction.response.defer()
                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, random.choice(self.messages))
                        for _ in range(5)
                    ]
                    await asyncio.gather(*tasks)
                return False

            if cid == "multi_spam_10x":
                await interaction.response.defer()
                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, random.choice(self.messages))
                        for _ in range(10)
                    ]
                    await asyncio.gather(*tasks)
                return False

            return True

    return MultipleSpamPanel()
