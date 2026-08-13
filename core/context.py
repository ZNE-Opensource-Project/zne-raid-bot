import discord
from discord.ext import commands


DENY_COLOR = 12395813
SUCCESS_COLOR = 5487909
WARN_COLOR = 12107045

DENY_EMOJI = "<:deny:1529732544189304923>"
SUCCESS_EMOJI = "<:approve:1529732623273037895>"
WARN_EMOJI = "<:warn:1529733126547308544>"

def deny_embed(message: str) -> discord.Embed:
    return discord.Embed(
        description=f"{DENY_EMOJI} {message}",
        color=DENY_COLOR)


def success_embed(message: str) -> discord.Embed:
    return discord.Embed(
        description=f"{SUCCESS_EMOJI} {message}",
        color=SUCCESS_COLOR)


def warn_embed(message: str) -> discord.Embed:
    return discord.Embed(
        description=f"{WARN_EMOJI} {message}",
        color=WARN_COLOR)


class Context(commands.Context):
    """Extended command context with standardized embed helpers."""

    def deny(self, message: str) -> discord.Embed:
        return deny_embed(message)

    def success(self, message: str) -> discord.Embed:
        return success_embed(message)

    def warn(self, message: str) -> discord.Embed:
        return warn_embed(message)


async def interaction_deny(self, message: str, **kwargs):
    return await self.send_message(
        embed=deny_embed(message), **kwargs)


async def interaction_success(self, message: str, **kwargs):
    return await self.send_message(
        embed=success_embed(message), **kwargs)


async def interaction_warn(self, message: str, **kwargs):
    return await self.send_message(
        embed=warn_embed(message), **kwargs)

discord.InteractionResponse.deny = interaction_deny
discord.InteractionResponse.success = interaction_success
discord.InteractionResponse.warn = interaction_warn

discord.Webhook.deny = interaction_deny
discord.Webhook.success = interaction_success
discord.Webhook.warn =interaction_warn
