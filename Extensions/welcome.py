import discord
from discord.ext import commands
from config import COLORS
from functions import get_timestamp


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
        async def on_member_join(self, member):
            """Wird ausgeführt, wenn ein neues Mitglied dem Server beitritt"""
            embed = discord.Embed(
                title="Willkommen auf dem Server!",
                description=f"Willkommen {member.mention} auf {member.guild.name}!",
                color=COLORS["green"],
                timestamp=get_timestamp()
            )
            embed.set_author(name=f"{member.name} ist der neue Mitglied", icon_url="https://flimando.com/logo.png")
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="📋 Erste Schritte", value="• Lies die Regeln\n• Stelle dich vor\n• Hab Spaß!", inline=False)
            embed.set_footer(text=f"Mitglied #{len(member.guild.members)}")
            channel = member.guild.get_channel(1029006771148312626)
            await channel.send(embed=embed)

        @commands.Cog.listener()
        async def on_member_remove(self, member):
            """Wird ausgeführt, wenn ein Mitglied den Server verlässt"""

            embed = discord.Embed(
                title="Verabschiedung",
                description=f"{member.mention} hat den Server verlassen.",
                color=COLORS["red"],
                timestamp=get_timestamp()
            )
            embed.set_author(name=f"{member.name} hat den Server verlassen", icon_url="https://flimando.com/logo.png")
            embed.set_thumbnail(url=member.display_avatar.url)
            channel = member.guild.get_channel(1029006771148312626)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
    print("Welcome Extension Loaded!")