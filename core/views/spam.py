import asyncio
import io
import aiohttp
import discord
import tomllib

from core.utils.helpers import ZNE_INVITE
from core.utils.db import get_global_default_message
from core.utils.helpers import send_message_http

with open("config.toml", "rb") as f:
    _config = tomllib.load(f)
DEFAULT_BUTTON_MESSAGE = _config["messages"]["og_msg"]


class SpamButton(discord.ui.LayoutView):
    def __init__(self, user_id: int, preset_content: str = None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.preset_content = preset_content
  
    container1 = discord.ui.Container(
        discord.ui.TextDisplay(content=f"# PRESS BUTTON TO START SPAM!\n-# zne is open source so it would be really appreciated if you could star the [github repo](https://github.com/ZNE-Opensource-Project/zne-raid-bot)"),
        discord.ui.ActionRow(
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="SPAM 5X",
                    custom_id="send_spam_button",
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="SPAM 6X",
                    custom_id="send_spam_button_6x",
                ),
        ),
        accent_colour=discord.Colour(16777215),
    )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data.get("custom_id") == "send_spam_button":
            await interaction.response.defer()

            if self.preset_content:
                msg = self.preset_content
            else:
                global_msg = await get_global_default_message()
                msg = global_msg if global_msg else DEFAULT_BUTTON_MESSAGE

            app_id = interaction.client.application_id
            token = interaction.token

            async with aiohttp.ClientSession() as session:
                tasks = [
                    send_message_http(session, app_id, token, msg)
                    for _ in range(5)
                ]
                await asyncio.gather(*tasks)

            return False

        if interaction.data.get("custom_id") == "send_spam_button_6x":
            await interaction.response.defer()

            if self.preset_content:
                msg = self.preset_content
            else:
                global_msg = await get_global_default_message()
                msg = global_msg if global_msg else DEFAULT_BUTTON_MESSAGE

            await interaction.followup.send(msg, ephemeral=False, allowed_mentions=discord.AllowedMentions(everyone=True))

            app_id = interaction.client.application_id
            token = interaction.token

            async with aiohttp.ClientSession() as session:
                tasks = [
                    send_message_http(session, app_id, token, msg)
                    for _ in range(5)
                ]
                await asyncio.gather(*tasks)

            return False
        return True


# Dynamic factory for custom spam button
def make_custom_spam_panel(user_id: int, message: str):
    class CustomSpamPanel(discord.ui.LayoutView):
        def __init__(self):
            super().__init__(timeout=None)
            self.custom_message = message

        container1 = discord.ui.Container(
        discord.ui.TextDisplay(content=f"# PRESS BUTTON TO START SPAM!\n-# you are spamming the following message:\n```{message}```"),
            discord.ui.ActionRow(
                    discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="SPAM 5X",
                        custom_id="custom_spam_send_button",
                    ),
                    discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="SPAM 6X",
                        custom_id="custom_spam_send_button_6x",
                    ),
            ),
        accent_colour=discord.Colour(16777215),
    )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data.get("custom_id") == "custom_spam_send_button":
                await interaction.response.defer()

                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, self.custom_message)
                        for _ in range(5)
                    ]
                    await asyncio.gather(*tasks)

                return False

            if interaction.data.get("custom_id") == "custom_spam_send_button_6x":
                await interaction.response.defer()

                await interaction.followup.send(self.custom_message, ephemeral=False, allowed_mentions=discord.AllowedMentions(everyone=True))

                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, self.custom_message)
                        for _ in range(5)
                    ]
                    await asyncio.gather(*tasks)

                return False
            return True

    return CustomSpamPanel()


# Dynamic factory for file spam panel
def make_filespam_panel(user_id: int, attachment: discord.Attachment):
    class FileSpamPanel(discord.ui.LayoutView):
        def __init__(self):
            super().__init__(timeout=None)
            self.attachment = attachment
            self.filename = attachment.filename
            self.url = attachment.url

        container1 = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"# file spam: {attachment.filename}\npress button to start file spam"),
                accessory=discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="Send",
                    custom_id="file_spam_send_button"
                )
            )
        )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data.get("custom_id") == "file_spam_send_button":
                await interaction.response.defer()

                file_bytes = await self.attachment.read()
                file = discord.File(fp=io.BytesIO(file_bytes), filename=self.filename)
                
                first_msg = await interaction.followup.send(file=file, ephemeral=False)
                
                attachment_url = None
                if first_msg.attachments:
                    attachment_url = first_msg.attachments[0].url
                
                if not attachment_url:
                    await interaction.followup.deny("Failed to get attachment URL", ephemeral=True)
                    return False

                app_id = interaction.client.application_id
                token = interaction.token

                async with aiohttp.ClientSession() as session:
                    tasks = [
                        send_message_http(session, app_id, token, attachment_url)
                        for _ in range(5)
                    ]
                    await asyncio.gather(*tasks)

                return False
            return True

    return FileSpamPanel()