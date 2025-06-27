"""
Unix-Befehle Extension für den Discord Bot

Funktionalitäten:
1. Clear Command
    - Löscht eine bestimmte Anzahl von Nachrichten
    - Verfügbar auf allen erlaubten Servern
    - Verzögertes Löschen zur Vermeidung von Rate Limits

2. Ban Command
    - Bannt einen Nutzer per Mention oder ID
    - Optionale Angabe eines Grundes
    - Nur für Admins/Moderatoren verfügbar
    - Logging des Vorgangs

3. Massenban Command
    - Bannt mehrere Nutzer gleichzeitig
    - IDs durch Kommas getrennt
    - Optionale Angabe eines Grundes
    - Ausführliche Erfolgs-/Fehlermeldungen

Sicherheitshinweise:
- Purge-Funktion sollte mit Bedacht verwendet werden
- Automatische Verzögerungen eingebaut
- Ephemeral Responses für bessere Übersicht
- Ban-Funktion nur für Berechtigte nutzbar
- Massenban nur für Administratoren
"""

from discord.ext import commands
import discord
import asyncio
from discord import app_commands
from functions import *
from config import COLORS, BOT_CONFIG, ALLOWED_GUILDS, GUILD_IDS, DISCORD_IDS

prefix = BOT_CONFIG["prefix"]

class Unix(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged Succesfully In")
        await self.bot.change_presence(status = discord.Status.online, activity=discord.Activity(type = discord.ActivityType.playing, name = "mit dem kleinen süssen Debian"))
    
    @app_commands.command(
        name="help",
        description="Zeigt die Hilfe an"
    )
    async def help(self, interaction: discord.Interaction, category: str = None):
        if interaction.guild_id not in ALLOWED_GUILDS["unix"]:
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        if interaction.guild_id == int(GUILD_IDS["flimando_admin"]):
            embed = discord.Embed(
                title="Hilfe - Befehle", 
                description="Hier sind die verfügbaren Befehle:", 
                color=COLORS["violet"], 
                timestamp=get_timestamp()
            )
            
            embed.add_field(name="/help", value="Ruft dieses Menü auf.", inline=False)
            embed.add_field(name="/clear", value="Löscht eine bestimmte Anzahl von Nachrichten.", inline=False)
            embed.add_field(name="/todo_add", value="Fügt Aufgaben zu einer To-Do-Liste hinzu.", inline=False)
            embed.add_field(name="/todo_delete", value="Löscht Aufgaben aus der To-Do-Liste.", inline=False)
            embed.add_field(name="/shop", value="Fügt Items zu einer Shopping-Liste hinzu.", inline=False)
            embed.add_field(name="/ashop", value="Löscht Items aus der Shopping-Liste.", inline=False)
            embed.add_field(name="/ports", value="Ruft eine Übersicht über die aktuelle Portfreigaben auf.", inline=False)
            embed.add_field(name="/gpt", value="Beantwortet Fragen über die OpenAI-API.", inline=False)
            embed.add_field(name="/ban", value="Bannt einen Nutzer vom Server (per Mention oder ID).", inline=False)
            embed.add_field(name="/massban", value="Bannt mehrere Nutzer gleichzeitig (per IDs).", inline=False)
            
            await interaction.response.send_message(embed=embed)
        elif interaction.guild_id == int(GUILD_IDS["flimando_server"]):
            embed = discord.Embed(
                title="Hilfe - Befehle", 
                description="Hier sind die verfügbaren Befehle:", 
                color=COLORS["violet"], 
                timestamp=get_timestamp()
            )
            embed.add_field(name="/help", value="Ruft dieses Menü auf.", inline=False)
            embed.add_field(name="/clear", value="Löscht eine bestimmte Anzahl von Nachrichten.", inline=False)
            embed.add_field(name="/ticket_info", value="Zeigt Informationen über ein Ticket an.", inline=False)
            embed.add_field(name="/setup_tickets", value="Erstellt das Ticket-System in einem bestimmten Kanal.", inline=False)
            embed.add_field(name="/ban", value="Bannt einen Nutzer vom Server (per Mention oder ID).", inline=False)
            embed.add_field(name="/massban", value="Bannt mehrere Nutzer gleichzeitig (per IDs).", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du befindest dich nicht in einem der Server, in denen du diesen Befehl benutzen kannst.", ephemeral=True)

    @app_commands.command(
        name = "clear",
        description = "Löscht eine bestimmte Anzahl von Nachrichten"
    ) #Kann überall benutzt werden weil nicht extrem wichtig
    async def clear(self, interaction: discord.Interaction, amount: int):
        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)
        
        # Warte kurz vor dem Purge
        await asyncio.sleep(1)
        
        # Führe Purge aus
        deleted = await interaction.channel.purge(limit=amount)
        
        # Warte nach dem Purge
        await asyncio.sleep(1)
        
        # Sende Bestätigung
        await interaction.followup.send(
            f"Die letzten {len(deleted)} Nachrichten wurden gelöscht",
            ephemeral=True
        )

    @app_commands.command(
        name = "ban",
        description = "Bannt einen Nutzer vom Server (per Mention oder ID)"
    )
    @app_commands.describe(
        user_id="Die ID des zu bannenden Nutzers (falls kein Nutzer ausgewählt)",
        user="Der zu bannende Nutzer",
        grund="Der Grund für den Bann",
        löschen_tage="Anzahl der Tage, für die Nachrichten gelöscht werden sollen (0-7)"
    )
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.User = None, user_id: str = None, grund: str = "Kein Grund angegeben", löschen_tage: int = 0):
        # Überprüfe Berechtigungen
        if not interaction.user.guild_permissions.ban_members and not any(role.id == DISCORD_IDS["admin_role"] or role.id == DISCORD_IDS["mod_role"] for role in interaction.user.roles):
            await interaction.response.send_message("Du hast keine Berechtigung zum Bannen von Nutzern!", ephemeral=True)
            return
            
        # Überprüfe ob löschen_tage im gültigen Bereich ist
        if löschen_tage < 0 or löschen_tage > 7:
            await interaction.response.send_message("Die Anzahl der Tage muss zwischen 0 und 7 liegen!", ephemeral=True)
            return
            
        # Überprüfe ob User ODER user_id angegeben wurde
        if user is None and user_id is None:
            await interaction.response.send_message("Du musst entweder einen Nutzer auswählen oder eine Nutzer-ID angeben!", ephemeral=True)
            return
            
        # Wenn user_id angegeben wurde, versuche den Nutzer zu finden
        if user_id is not None:
            try:
                user_id_int = int(user_id)
                user = await self.bot.fetch_user(user_id_int)
            except (ValueError, discord.NotFound):
                await interaction.response.send_message(f"Konnte keinen Nutzer mit der ID {user_id} finden!", ephemeral=True)
                return
                
        # Überprüfe ob User der Bot selbst ist
        if user.id == self.bot.user.id:
            await interaction.response.send_message("Ich kann mich nicht selbst bannen! 😢", ephemeral=True)
            return
            
        # Überprüfe ob User der Server-Owner ist
        if user.id == interaction.guild.owner_id:
            await interaction.response.send_message("Ich kann den Server-Eigentümer nicht bannen!", ephemeral=True)
            return
            
        # Überprüfe ob User bereits gebannt ist
        try:
            ban_entry = await interaction.guild.fetch_ban(user)
            await interaction.response.send_message(f"Der Nutzer {user.name} (ID: {user.id}) ist bereits gebannt!", ephemeral=True)
            return
        except discord.NotFound:
            pass
            
        # Erstelle ein Embed für die Ban-Bestätigung
        ban_embed = discord.Embed(
            title="🔨 Ban ausgeführt",
            description=f"**Nutzer:** {user.name} (ID: {user.id})\n**Grund:** {grund}",
            color=COLORS["red"],
            timestamp=get_timestamp()
        )
        ban_embed.set_thumbnail(url=user.display_avatar.url)
        ban_embed.add_field(name="Gebannt von", value=interaction.user.mention, inline=False)
        
        # Ban ausführen
        try:
            await interaction.guild.ban(user, reason=f"Gebannt von {interaction.user.name}: {grund}", delete_message_days=löschen_tage)
            await interaction.response.send_message(embed=ban_embed)
            
            # Versuche dem Nutzer eine DM zu senden
            try:
                dm_embed = discord.Embed(
                    title=f"Du wurdest von {interaction.guild.name} gebannt",
                    description=f"**Grund:** {grund}",
                    color=COLORS["red"],
                    timestamp=get_timestamp()
                )
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                # Nutzer hat DMs deaktiviert oder blockiert den Bot
                pass
                
        except discord.Forbidden:
            await interaction.response.send_message("Ich habe nicht die Berechtigung, diesen Nutzer zu bannen!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Fehler beim Bannen: {str(e)}", ephemeral=True)

    @app_commands.command(
        name = "massban",
        description = "Bannt mehrere Nutzer gleichzeitig (per IDs)"
    )
    @app_commands.describe(
        user_ids="Durch Komma getrennte Liste von Nutzer-IDs (z.B. 123456789,987654321)",
        grund="Der Grund für den Bann",
        löschen_tage="Anzahl der Tage, für die Nachrichten gelöscht werden sollen (0-7)"
    )
    @app_commands.default_permissions(administrator=True)
    async def massban(self, interaction: discord.Interaction, user_ids: str, grund: str = "Kein Grund angegeben", löschen_tage: int = 0):
        # Überprüfe Berechtigungen (nur für Admins)
        if not interaction.user.guild_permissions.administrator and not any(role.id == DISCORD_IDS["admin_role"] for role in interaction.user.roles):
            await interaction.response.send_message("Du benötigst Administrator-Rechte für den Massenban!", ephemeral=True)
            return
            
        # Überprüfe ob löschen_tage im gültigen Bereich ist
        if löschen_tage < 0 or löschen_tage > 7:
            await interaction.response.send_message("Die Anzahl der Tage muss zwischen 0 und 7 liegen!", ephemeral=True)
            return
            
        # Überprüfe, ob überhaupt IDs angegeben wurden
        if not user_ids or user_ids.strip() == "":
            await interaction.response.send_message("Du musst mindestens eine Nutzer-ID angeben!", ephemeral=True)
            return
            
        # Defer response für längere Verarbeitung
        await interaction.response.defer(ephemeral=False)
        
        # Splitte die IDs und entferne Leerzeichen
        id_list = [id.strip() for id in user_ids.split(",")]
        
        # Statistik-Tracking
        erfolgreiche_bans = []
        fehlgeschlagene_bans = []
        bereits_gebannt = []
        nicht_gefunden = []
        
        # Progress-Embed
        progress_embed = discord.Embed(
            title="⏳ Massenban wird ausgeführt...",
            description=f"Verarbeite {len(id_list)} Nutzer-IDs...",
            color=COLORS["orange"],
            timestamp=get_timestamp()
        )
        progress_message = await interaction.followup.send(embed=progress_embed)
        
        # Verarbeite jeden Nutzer
        for user_id in id_list:
            try:
                # Versuche die ID zu konvertieren
                user_id_int = int(user_id)
                
                # Versuche den Nutzer zu finden
                try:
                    user = await self.bot.fetch_user(user_id_int)
                    
                    # Überprüfe auf spezielle Fälle
                    if user.id == self.bot.user.id:
                        fehlgeschlagene_bans.append(f"{user.name} (ID: {user.id}) - Kann Bot nicht bannen")
                        continue
                        
                    if user.id == interaction.guild.owner_id:
                        fehlgeschlagene_bans.append(f"{user.name} (ID: {user.id}) - Kann Server-Owner nicht bannen")
                        continue
                    
                    # Überprüfe ob User bereits gebannt ist
                    try:
                        ban_entry = await interaction.guild.fetch_ban(user)
                        bereits_gebannt.append(f"{user.name} (ID: {user.id})")
                        continue
                    except discord.NotFound:
                        pass
                    
                    # Ban ausführen
                    await interaction.guild.ban(user, reason=f"Massenban von {interaction.user.name}: {grund}", delete_message_days=löschen_tage)
                    erfolgreiche_bans.append(f"{user.name} (ID: {user.id})")
                    
                    # Versuche dem Nutzer eine DM zu senden
                    try:
                        dm_embed = discord.Embed(
                            title=f"Du wurdest von {interaction.guild.name} gebannt",
                            description=f"**Grund:** {grund}",
                            color=COLORS["red"],
                            timestamp=get_timestamp()
                        )
                        await user.send(embed=dm_embed)
                    except:
                        pass
                    
                    # Kurze Pause um Rate Limits zu vermeiden
                    await asyncio.sleep(0.5)
                    
                except discord.NotFound:
                    nicht_gefunden.append(user_id)
                except Exception as e:
                    fehlgeschlagene_bans.append(f"ID: {user_id} - Fehler: {str(e)}")
                    
            except ValueError:
                nicht_gefunden.append(user_id)
                
        # Erstelle ein Embed für die Zusammenfassung
        result_embed = discord.Embed(
            title="🔨 Massenban abgeschlossen",
            description=f"**Grund:** {grund}\n**Durchgeführt von:** {interaction.user.mention}",
            color=COLORS["green"],
            timestamp=get_timestamp()
        )
        
        # Füge Statistiken hinzu
        result_embed.add_field(
            name=f"✅ Erfolgreich gebannt ({len(erfolgreiche_bans)})",
            value="\n".join(erfolgreiche_bans[:10]) + (f"\n... und {len(erfolgreiche_bans) - 10} weitere" if len(erfolgreiche_bans) > 10 else "") if erfolgreiche_bans else "Keine",
            inline=False
        )
        
        if bereits_gebannt:
            result_embed.add_field(
                name=f"⚠️ Bereits gebannt ({len(bereits_gebannt)})",
                value="\n".join(bereits_gebannt[:5]) + (f"\n... und {len(bereits_gebannt) - 5} weitere" if len(bereits_gebannt) > 5 else ""),
                inline=False
            )
            
        if nicht_gefunden:
            result_embed.add_field(
                name=f"❓ Nicht gefunden ({len(nicht_gefunden)})",
                value="\n".join(nicht_gefunden[:5]) + (f"\n... und {len(nicht_gefunden) - 5} weitere" if len(nicht_gefunden) > 5 else ""),
                inline=False
            )
            
        if fehlgeschlagene_bans:
            result_embed.add_field(
                name=f"❌ Fehlgeschlagen ({len(fehlgeschlagene_bans)})",
                value="\n".join(fehlgeschlagene_bans[:5]) + (f"\n... und {len(fehlgeschlagene_bans) - 5} weitere" if len(fehlgeschlagene_bans) > 5 else ""),
                inline=False
            )
            
        # Sende das finale Embed
        await progress_message.edit(embed=result_embed)










async def setup(bot):
    await bot.add_cog(Unix(bot))
    print("Unix Extension Loaded!")
