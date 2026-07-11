import discord
import os
import io
import json
import time
import random
from datetime import datetime, timezone

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

ALTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'alts'))

def get_color(color_str):
    if isinstance(color_str, str) and color_str.upper() == 'RANDOM':
        return discord.Color.random()
    return discord.Color(color_str)

def cog_setup(bot):
    @bot.command(name='gen', aliases=['get', 'generator'])
    async def _gen(ctx, *args):

        if ctx.channel.id != int(config['GenChannelID']):
            return await ctx.reply(embed=discord.Embed(
                title=f"Error {config['ErrorEmoji']}",
                description=f"**ERROR!** This command can only be used in <#{config['GenChannelID']}> - {ctx.author}",
                color=get_color(config['Color'])
            ).set_footer(text=f"Requested by {ctx.author} "))

        user = ctx.author
        timeout = int(config['GenCooldown'])
        import database as db_module
        has_bypass_role = 1496816334837907567 in [r.id for r in ctx.author.roles]

        if not has_bypass_role:
            author = db_module.db.get(f'ae_{ctx.author.id}_{user.id}')
            if author is not None and timeout - (time.time() * 1000 - int(author)) > 0:
                remaining = timeout - (time.time() * 1000 - int(author))
                minutes = int(remaining // 60000)
                seconds = int((remaining % 60000) // 1000)
                return await ctx.reply(embed=discord.Embed(
                    title=f"Error {config['ErrorEmoji']}",
                    description=f"You are genning too fast. Wait **{minutes}m and {seconds}s ** to able to gen again!",
                    color=get_color(config['Color'])
                ).set_footer(text=f"Requested by {ctx.author} "))

        if not args:
            return await ctx.send(embed=discord.Embed(
                title=f"Error {config['ErrorEmoji']}",
                description=f"Specify the name of the service you want to generate. \n\n Example: `{config['prefix']}gen pornhub`",
                color=get_color(config['Color'])
            ).set_footer(text=f"Requested by {ctx.author} "))

        stock_folder = os.path.join(ALTS_DIR, args[0])
        if not os.path.isdir(stock_folder):
            return await ctx.reply(embed=discord.Embed(
                description="This category does not exist, check the stock!",
                color=get_color(config['Color'])
            ).set_footer(text=f"Requested by {ctx.author} "))

        all_files = []
        for root, dirs, files in os.walk(stock_folder):
            for f in files:
                full = os.path.join(root, f)
                if os.path.isfile(full):
                    all_files.append(full)

        if not all_files:
            nostock_embed = discord.Embed(
                title=f"Error {config['ErrorEmoji']} | Out of stock",
                description=f"There are no accounts for **{args[0]}** Check the stock carefully!",
                color=get_color(config['Color'])
            ).set_footer(text=f"Requested by {ctx.author} ")
            return await ctx.reply(embed=nostock_embed)

        chosen = random.choice(all_files)
        file_path = chosen
        rel_sub = os.path.relpath(os.path.dirname(chosen), stock_folder)
        type_name = args[0] if rel_sub == '.' else f"{args[0]}/{rel_sub.replace(os.sep, '/')}"

        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()

        first_line = data.split('\n')[0]
        error_msg = "An error occurred while generating your account! Please report this issue in a ticket!"

        if first_line == '':
            first_line = error_msg

        r_embed = discord.Embed(
            title=f"Your **{args[0]}** account has been sent to you in private message!",
            color=0x2CFF00
        ).set_footer(text=f"Requested by {ctx.author} ")

        embed = discord.Embed(
            title=f"Here is your **__{args[0]}__** account from {ctx.guild.name}",
            color=get_color(config['Color']),
            timestamp=datetime.now(timezone.utc)
        ).set_footer(text=f"Requested by {ctx.author} ")

        if len(data) > 2000:
            embed.description = f"**TYPE: {type_name}**\nThe account is too long to display here, so it has been sent as a file attachment."
            account_file = discord.File(io.BytesIO(data.encode('utf-8')), filename=f"{args[0]}.txt")
        else:
            embed.description = f"**TYPE: {type_name}**\n```{data}```"
            account_file = None

        os.remove(file_path)

        if not has_bypass_role:
            db_module.db.set(f'ae_{ctx.author.id}_{user.id}', int(time.time() * 1000))

        try:
            if account_file is not None:
                await ctx.author.send(embed=embed, file=account_file)
            else:
                await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"{config['ErrorEmoji']} | Your private messages are disabled, I cannot send you a message. (ignore the other messages.)")
        await ctx.send(ctx.author.mention)
        await ctx.send(embed=r_embed)
