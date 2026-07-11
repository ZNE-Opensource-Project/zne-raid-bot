import discord
import os
import aiohttp
import asyncio
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALTS_DIR = os.path.join(BASE_DIR, '..', 'alts')

def cog_setup(bot):
    @bot.command(name='oldrestock', aliases=['addalts'])
    async def _oldrestock(ctx, type_name: str = None, alt: str = None):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(title="You don't have permission to use this command!", color=bot.color))
        if not type_name or not alt:
            return await ctx.send(embed=discord.Embed(title=f"Usage: {bot.prefix}restock (type) (accounts)", color=bot.color))
        bot.gen.add_alt(type_name, alt)
        await ctx.send(embed=discord.Embed(title=f"Added {type_name} Accounts!", color=bot.color))

    @bot.command(name='restock', aliases=['restonk', 'restocks', 'restonks'])
    async def _restock(ctx, *args):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send('Nah you cant do that!')

        os.makedirs(ALTS_DIR, exist_ok=True)

        if ctx.message.attachments:
            stonks = args[0] if args else None
            if not stonks:
                return await ctx.send('Which type i have to restock...')
            restockable = os.path.join(ALTS_DIR, f'{stonks}.txt')

            attachment = ctx.message.attachments[0]
            url = attachment.url

            fd, temp_path = tempfile.mkstemp(suffix='.tmp', dir=ALTS_DIR)
            os.close(fd)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            with open(temp_path, 'wb') as f:
                                f.write(await response.read())
                        else:
                            os.remove(temp_path)
                            return await ctx.send('Failed to download file.')

                with open(temp_path, 'r', encoding='utf-8') as f:
                    data = f.read()
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            with open(restockable, 'a', encoding='utf-8') as f:
                f.write(f'{data}\n')

            accs = len(data.split('\n'))
            await ctx.send(f" <a:success:899665242043338812>  | Restocked **{stonks.upper()}** with `{accs}` accounts!")
        else:
            restockable = os.path.join(ALTS_DIR, f'{args[0]}.txt')
            accounts = ' '.join(args[1:])
            if not accounts:
                return await ctx.send('Please provide something.')
            with open(restockable, 'a', encoding='utf-8') as f:
                f.write(f'{accounts}\n')
            accountss = accounts.split('\n')
            await ctx.send(f" <a:check:875142764906577940>  | Restocked **{len(accountss)}** accounts for **__{args[0].upper()}__**")

        async def delayed_delete():
            await asyncio.sleep(2)
            await ctx.message.delete()

        bot.loop.create_task(delayed_delete())

    @bot.command(name='unstock', aliases=['destock', 'removestock', 'removestonks'])
    async def _unstock(ctx, stonks: str = None):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send('Nah you cant do that!')
        if not stonks:
            return await ctx.send('Which type i have to delete...')
        restockable = os.path.join(ALTS_DIR, f'{stonks}.txt')
        try:
            os.remove(restockable)
            await ctx.send(f" <a:success:899665242043338812>  | Deleted file for **__{stonks.upper()}__**")
        except FileNotFoundError:
            await ctx.send(f"Failed to delete the **__{stonks.upper()}__. Please make sure that the file exists.")

    @bot.command(name='stock', aliases=[])
    async def _stock(ctx):
        stock_arr = bot.gen.calculate_stock()
        content = "# ZNEGEN Stocks!\nif any stocks say `0` please contact voby7 (`vd1n`) to restock unless there is already a reason.\n"
        for item in stock_arr:
            content += f"**{item[0]}** = `{item[1]}`\n"

        class _StockView(discord.ui.LayoutView):
            container1 = discord.ui.Container(
                discord.ui.TextDisplay(content=content),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(content="-# made by voby7"),
            )

        await ctx.send(view=_StockView())

    @bot.command(name='bulkrestock', aliases=[])
    async def _bulkrestock(ctx, type_name: str = None, *alts):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=discord.Embed(title="You don't have permission to use this command!", color=bot.color))
        if not type_name or not alts:
            return await ctx.send(embed=discord.Embed(title=f"Usage: {bot.prefix}restock <type> <alts> (alts split with ,)", color=bot.color))
        for alt in alts:
            bot.gen.add_alt(type_name, alt)
        await ctx.send(embed=discord.Embed(title=f"Added {len(alts)} {type_name} alts!", color=bot.color))
