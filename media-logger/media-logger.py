from datetime import datetime

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class MediaLogger(commands.Cog):
    """Logs all media to a specified channel"""
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.plugin_db.get_partition(self)

    async def log_channel(self):
        config = await self.db.find_one({'_id': 'config'}) or {}
        channel_id = config.get('log_channel')
        if channel_id:
            return self.bot.get_channel(int(channel_id))

    @commands.Cog.listener()
    async def on_message(self, m):
        if m.author.bot: return

        em = discord.Embed(
            description=f"**Media Posted**: [Jump to image]({m.jump_url}).',
            color=self.bot.main_color,
            timestamp=datetime.utcnow()
        )
        em.set_footer(text=f'Author: {m.author.id} | Message ID: {m.id}')
        for a in m.attachments:
            if a.filename.endswith('.png') or a.filename.endswith('.jpeg') or a.filename.endswith('.gif') or a.filename.endswith('.mp4') or a.filename.endswith('.jpg'):
                file = await a.to_file()
                channel = await self.log_channel()
                if channel:
                    await channel.send(embed=em)

    @checks.has_permissions(PermissionLevel.OWNER)
    @commands.command()
    async def setmedialogchannel(self, ctx, channel: discord.TextChannel):
        """Sets the media log channel"""
        await self.db.find_one_and_update({'_id': 'config'}, {'$set': {'log_channel': str(channel.id)}}, upsert=True)
        await ctx.send('Updated!',delete_after=20)


def setup(bot):
    bot.add_cog(MediaLogger(bot))
