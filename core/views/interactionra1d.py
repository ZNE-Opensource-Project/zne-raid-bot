import asyncio
import aiohttp
import discord
import tomllib

from core.utils.helpers import ZNE_INVITE, send_message_http
from core.utils.db import get_global_default_message

with open("config.toml", "rb") as f:
    _config = tomllib.load(f)
DEFAULT_BUTTON_MESSAGE = _config["messages"]["og_msg"]

stored_tokens: list[tuple[int, str]] = []
interaction_raid_original_message: discord.Message | None = None


def make_interaction_raid_view(original_message: discord.Message | None = None):
    global interaction_raid_original_message
    if original_message is not None:
        interaction_raid_original_message = original_message

    token_count = len(stored_tokens)
    msg_count = token_count * 5

    class DynamicView(discord.ui.LayoutView):
        def __init__(self):
            super().__init__(timeout=None)
            self.original_message = original_message

        container1 = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"## Interaction Raid\n-# **messages you can spam**: `{msg_count}`\n-# **stored webhooks**: `{token_count}`"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Farm",
                    custom_id="farm_1",
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Farm",
                    custom_id="farm_2",
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Farm",
                    custom_id="farm_3",
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="More Buttons",
                    custom_id="more_buttons",
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.danger,
                    label="START SPAM",
                    custom_id="start_spam",
                ),
            ),
            accent_colour=discord.Colour(16777215),
        )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            custom_id = interaction.data.get("custom_id")

            if custom_id in ("farm_1", "farm_2", "farm_3"):
                await interaction.response.defer()
                app_id = interaction.client.application_id
                token = interaction.token
                stored_tokens.append((app_id, token))

                if self.original_message:
                    new_view = make_interaction_raid_view(self.original_message)
                    await self.original_message.edit(view=new_view)

                return False

            if custom_id == "more_buttons":
                await interaction.response.defer()
                for _ in range(5):
                    await interaction.followup.send(
                        view=make_single_farm_panel(),
                        ephemeral=True,
                    )
                return False

            if custom_id == "start_spam":
                await interaction.response.defer()

                if not stored_tokens:
                    await interaction.followup.send(
                        "No tokens stored! Click Farm buttons first.",
                        ephemeral=True,
                    )
                    return False

                global_msg = await get_global_default_message()
                msg = global_msg if global_msg else DEFAULT_BUTTON_MESSAGE

                token_count = len(stored_tokens)

                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for token_app_id, token in stored_tokens:
                        for _ in range(5):
                            tasks.append(send_message_http(session, token_app_id, token, msg))
                    await asyncio.gather(*tasks)

                stored_tokens.clear()

                if self.original_message:
                    new_view = make_interaction_raid_view(self.original_message)
                    await self.original_message.edit(view=new_view)

                await interaction.followup.send(
                    f"Sent {token_count * 5} messages!",
                    ephemeral=True,
                )
                return False

            return True

    return DynamicView()


def make_single_farm_panel():
    class SingleFarmButton(discord.ui.LayoutView):
        def __init__(self):
            super().__init__(timeout=None)

        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content="## Farm Token\nClick to store interaction token"),
            discord.ui.ActionRow(
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Farm",
                    custom_id="single_farm",
                ),
            ),
            accent_colour=discord.Colour(16777215),
        )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data.get("custom_id") == "single_farm":
                await interaction.response.defer()
                app_id = interaction.client.application_id
                token = interaction.token
                stored_tokens.append((app_id, token))

                if interaction_raid_original_message:
                    new_view = make_interaction_raid_view(interaction_raid_original_message)
                    await interaction_raid_original_message.edit(view=new_view)

                return False
            return True

    return SingleFarmButton()


InteractionRaidView = make_interaction_raid_view
