"""
Ticket-System Extension für den Discord Bot

Hauptfunktionen:
1. Ticket-Erstellung
    - Kategoriebasierte Tickets mit Cooldown
    - Automatische Berechtigungsverwaltung
    - Logging aller Aktionen

2. Ticket-Verwaltung
    - Schließen von Tickets
    - Archivierung
    - Berechtigungsprüfung
    - Ticket-Statistiken

3. Ticket-Tracking
    - Speicherung von Ticket-Metadaten
    - Besitzer-Verwaltung
    - Erstellungszeitpunkt-Tracking
    - Aktions-Logging

Berechtigungssystem:
- Admin/Mod-Rollen haben volle Rechte
- Ticket-Ersteller können nur eigene Tickets schließen

Logging:
- Alle Aktionen werden in ticket_logs.json gespeichert
- Format: {timestamp, action, user_id, ticket_id, details}

Cooldown:
- 60 Sekunden zwischen Ticket-Erstellungen pro User(wenn nicht in Beta)
"""

import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
from functions import *
from config import COLORS, DISCORD_IDS, ALLOWED_GUILDS
from typing import Optional
import json
import time
from datetime import datetime, timedelta
from threading import Lock
from collections import defaultdict

# Konstanten
ADMIN_ROLE_ID = DISCORD_IDS["admin_role"]
MOD_ROLE_ID = DISCORD_IDS["mod_role"]
TICKET_CATEGORY_ID = DISCORD_IDS["ticket_category"]
TICKET_CHANNEL_ID = DISCORD_IDS["ticket_channel"]
if BOT_CONFIG["beta"] == True:
    TICKET_COOLDOWN = 1  # 1 Sekunde
else:
    TICKET_COOLDOWN = 60  # 1 Minute

class CooldownManager:
    def __init__(self, cooldown_time: int = TICKET_COOLDOWN):
        self.cooldown_time = cooldown_time
        self.cooldowns = defaultdict(int)
        self._lock = Lock()
        
    def check_cooldown(self, user_id: int) -> bool:
        """Prüft und updated den Cooldown für einen User"""
        with self._lock:
            now = time.time()
            # Cleanup alte Einträge
            if len(self.cooldowns) > 1000:  # Beispiel-Grenze
                self.cleanup_cooldowns()
                
            last_use = self.cooldowns.get(user_id, 0)
            if now - last_use >= self.cooldown_time:
                self.cooldowns[user_id] = now
                return True
            return False
    
    def cleanup_cooldowns(self):
        """Entfernt abgelaufene Cooldowns"""
        now = time.time()
        expired = [
            user_id for user_id, timestamp in self.cooldowns.items()
            if now - timestamp >= self.cooldown_time
        ]
        for user_id in expired:
            del self.cooldowns[user_id]

def log_ticket_action(action: str, user_id: int, user_name: str, ticket_id: int, details: str):
    """Loggt eine Ticket-Aktion in die Log-Datei"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id,
        "user_name": user_name,
        "ticket_id": ticket_id,
        "details": details
    }
    
    try:
        with open('ticket_logs.json', 'r+') as f:
            logs = json.load(f)
            logs.append(log_entry)
            f.seek(0)
            json.dump(logs, f, indent=4)
    except FileNotFoundError:
        with open('ticket_logs.json', 'w') as f:
            json.dump([log_entry], f, indent=4)

class TicketControlButtons(discord.ui.View):
    """Stellt Kontrollbuttons für Tickets bereit."""
    
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket Claimen", style=discord.ButtonStyle.green, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not any(role.id in [DISCORD_IDS["admin_role"], DISCORD_IDS["mod_role"]] for role in interaction.user.roles):
                await interaction.response.send_message("Sie haben keine Berechtigung für diese Aktion.", ephemeral=True)
                return

            embed = interaction.message.embeds[0]
            embed.add_field(name="Bearbeiter", value=f"{interaction.user.mention}", inline=False)
            await interaction.message.edit(embed=embed)
            await interaction.response.send_message(f"Ticket wurde von {interaction.user.mention} übernommen.", ephemeral=False)
            self.children[0].disabled = True
            await interaction.message.edit(view=self)

            # Logging einbauen
            log_ticket_action(
                "CLAIM", 
                interaction.user.id,
                interaction.user.name,
                interaction.channel.id,
                f"Ticket wurde von {interaction.user} übernommen"
            )
        except Exception as e:
            print(f"Fehler beim Claimen: {e}")
            await interaction.response.send_message("Es ist ein Fehler aufgetreten.", ephemeral=True)

    @discord.ui.button(label="Ticket Schließen", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Berechtigungsprüfung
            if not any(role.id in [DISCORD_IDS["admin_role"], DISCORD_IDS["mod_role"]] for role in interaction.user.roles):
                ticket_owner_id = get_ticket_owner(interaction.channel.id)
                if interaction.user.id != ticket_owner_id:
                    await interaction.response.send_message("Sie verfügen nicht über die erforderlichen Berechtigungen.", ephemeral=True)
                    return

            await interaction.response.send_message("Das Ticket wird geschlossen...", ephemeral=False)
        
            # Hole Ticket-Daten
            ticket_data = get_ticket_data(interaction.channel.id)
            if not ticket_data:
                await interaction.followup.send("Fehler: Ticket-Daten konnten nicht gefunden werden.", ephemeral=True)
                return
            
            # Ändere Kanal-Berechtigungen, the cake is a lie
            ticket_owner = interaction.guild.get_member(ticket_data["Owner_ID"])
            await interaction.channel.set_permissions(ticket_owner, read_messages=False)
        
            # Wähle die richtige Archiv-Kategorie basierend auf dem Ticket-Typ
            if ticket_data["Type"] == "🚫 Entbannungsantrag":
                archive_category = interaction.guild.get_channel(DISCORD_IDS["old_unban_category"])
            else:
                archive_category = interaction.guild.get_channel(DISCORD_IDS["closed_category"])

            if not archive_category:
                await interaction.followup.send("Archiv-Kategorie nicht gefunden!", ephemeral=True)
                return
        
            # Verschiebe in die entsprechende Kategorie
            await interaction.channel.edit(
                category=archive_category,
                name=f"closed-{interaction.channel.name}"
            )
        
            # Sende Abschluss-Embed mit neuem View
            close_embed = discord.Embed(
                title="Ticket Geschlossen",
                description=f"Ticket wurde von {interaction.user.mention} geschlossen.\n"
                           f"Ursprünglicher Ersteller: {ticket_owner.mention}\n"
                           f"Ticket-Typ: {ticket_data['Type']}\n"
                           f"Erstellt am: {ticket_data['Created']}",
                color=COLORS["red"]
            )
            await interaction.message.edit(view=None)  # Alte Buttons entfernen
            await interaction.channel.send(embed=close_embed, view=ArchivedTicketButtons())
        
            # Entferne aus der Datenbank
            kill_ticket(interaction.channel.id)

            # Logging
            log_ticket_action(
                "CLOSE",
                interaction.user.id,
                interaction.user.name,
                interaction.channel.id,
                f"Ticket wurde von {interaction.user} geschlossen"
            )

        except Exception as e:
            print(f"Fehler beim Schließen: {e}")
            await interaction.followup.send("Es ist ein Fehler beim Schließen des Tickets aufgetreten.", ephemeral=True)

class ArchivedTicketButtons(discord.ui.View):
    """Kontrollbuttons für archivierte Tickets."""
    
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket Löschen", style=discord.ButtonStyle.red, custom_id="delete_ticket")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Admin-Check
            if not any(role.id == DISCORD_IDS["admin_role"] for role in interaction.user.roles):
                await interaction.response.send_message(
                    "Brudi, du brauchst Admin-Rechte um Tickets zu löschen! KEKW", 
                    ephemeral=True
                )
                return

            await interaction.response.send_message("Ticket wird gelöscht...", ephemeral=False)
            
            # Logging
            log_ticket_action(
                "DELETE",
                interaction.user.id,
                interaction.user.name,
                interaction.channel.id,
                f"Ticket wurde von {interaction.user} gelöscht"
            )
            
            # Channel löschen
            await interaction.channel.delete()

        except Exception as e:
            print(f"Fehler beim Löschen des Tickets: {e}")
            await interaction.followup.send(
                "Ups, da ist etwas schief gelaufen beim Löschen!", 
                ephemeral=True
            )

class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown_manager = CooldownManager()

    @discord.ui.button(label="🛒 Server Kauf", style=discord.ButtonStyle.red, custom_id="server_kauf")
    async def server_kauf(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_ticket(interaction, "🛒 Server Kauf")

    @discord.ui.button(label="🔧 Technischer Support", style=discord.ButtonStyle.green, custom_id="tech_support")
    async def tech_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_ticket(interaction, "🔧 Technischer Support")

    @discord.ui.button(label="❓ Allgemeiner Support", style=discord.ButtonStyle.blurple, custom_id="allg_support")
    async def allg_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_ticket(interaction, "❓ Allgemeiner Support")

    @discord.ui.button(label="🚫 Entbannungsantrag", style=discord.ButtonStyle.gray, custom_id="unban_request")
    async def unban_request(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_ticket(interaction, "🚫 Entbannungsantrag")

    async def handle_ticket(self, interaction: discord.Interaction, ticket_type: str):
        try:

            # Cooldown and Max Tickets Check
            if not self.cooldown_manager.check_cooldown(interaction.user.id):
                await interaction.response.send_message(
                    f"Bitte warten Sie {TICKET_COOLDOWN} Sekunden, bevor Sie ein neues Ticket erstellen können.",
                    ephemeral=True
                )
                return

            if not max_tickets(interaction.user.id):
                await interaction.response.send_message(
                    "Sie haben bereits die maximale Anzahl an offenen Tickets erreicht. Bitte kontaktieren Sie einen Administrator, falls Sie weitere Tickets benötigen.", 
                    ephemeral=True
                )
                return

            # Erstelle Kanal-Berechtigungen
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.get_role(MOD_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            # Erstelle den Ticket-Kanal
            if ticket_type == "🚫 Entbannungsantrag":
                channel = await interaction.guild.create_text_channel(
                    name=f"unban-{interaction.user.name}",
                    category=interaction.guild.get_channel(TICKET_CATEGORY_ID),
                    overwrites=overwrites
                )
            else:
                channel = await interaction.guild.create_text_channel(
                    name=f"ticket-{interaction.user.name}",
                    category=interaction.guild.get_channel(TICKET_CATEGORY_ID),
                    overwrites=overwrites
                )

            # Erstelle das Ticket in der Datenbank
            ticket_data = {
                "Owner_ID": interaction.user.id,
                "Type": ticket_type,
                "Created": str(get_timestamp()),
                "Status": "Open",
                "message_id": None  # Wird später gesetzt
            }
            create_ticket(channel.id, interaction.user.id, ticket_type)

            # Sende Bestätigungsnachricht
            await interaction.response.send_message(
                f"Dein Ticket wurde erstellt: {channel.mention}",
                ephemeral=True
            )

            # Erstelle ticket-spezifische Beschreibung
            if ticket_type == "🛒 Server Kauf":
                description = (f"Willkommen {interaction.user.mention}!\n\n"
                            "Bitte teilen Sie uns mit:\n"
                            "• Welches Server-Paket möchten Sie kaufen?\n"
                            "• Gewünschte Zahlungsmethode?\n"
                            "• Haben Sie spezielle Anforderungen?\n\n"
                            "Ein Teammitglied wird sich in Kürze um Ihre Anfrage kümmern.")
            
            elif ticket_type == "🔧 Technischer Support":
                description = (f"Willkommen {interaction.user.mention}!\n\n"
                            "Bitte beschreiben Sie Ihr technisches Problem:\n"
                            "• Was genau funktioniert nicht?\n"
                            "• Seit wann besteht das Problem?\n"
                            "• Welche Fehlermeldungen erscheinen?\n\n"
                            "Unser Support-Team wird Ihnen schnellstmöglich helfen.")
            
            elif ticket_type == "🚫 Entbannungsantrag":
                description = (f"Willkommen {interaction.user.mention}!\n\n"
                            "Bitte geben Sie uns folgende Informationen für Ihren Entbannungsantrag:\n"
                            "• Ihr Minecraft-Username\n"
                            "• Grund des Banns\n"
                            "• Wann wurden Sie gebannt?\n"
                            "• Warum sollten wir Sie entbannen?\n"
                            "• Was haben Sie aus der Situation gelernt?\n\n"
                            "Ein Teammitglied wird Ihren Antrag prüfen und sich bei Ihnen melden.")
            
            else:  # Allgemeiner Support
                description = (f"Willkommen {interaction.user.mention}!\n\n"
                            "Bitte schildern Sie Ihr Anliegen möglichst genau.\n"
                            "Je mehr Details Sie uns geben, desto besser können wir Ihnen helfen!\n\n"
                            "Ein Teammitglied wird sich in Kürze um Ihre Anfrage kümmern.")

            # Erstelle das initiale Embed mit Kontroll-Buttons
            embed = discord.Embed(
                title=f"Ticket: {ticket_type}",
                description=description,
                color=COLORS["green"]
            )
            embed.add_field(name="Ticket-Ersteller", value=interaction.user.mention, inline=False)
            
            # Sende das Embed mit den Kontroll-Buttons
            message = await channel.send(embed=embed, view=TicketControlButtons())
            await channel.send(f"{interaction.guild.get_role(1028682945810137188).mention}")
            # Speichere die Message-ID
            ticket_data = get_ticket_data(channel.id)
            if ticket_data:
                ticket_data["message_id"] = message.id
                dump()  # Speichere die Änderungen

            # Logging nach erfolgreicher Erstellung
            log_ticket_action(
                "CREATE",
                interaction.user.id,
                interaction.user.name,
                channel.id,
                f"Neues Ticket erstellt vom Typ {ticket_type}"
            )

        except Exception as e:
            print(f"Fehler bei Ticket-Erstellung: {e}")
            await interaction.response.send_message("Es tut uns leid, das Ticket konnte nicht erstellt werden.", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_manager = CooldownManager()
        self.ctx_menu = app_commands.ContextMenu(
            name='Ticket Informationen',
            callback=self.ticket_info_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the cog is ready."""
        print(f"{self.__class__.__name__} Cog has been loaded")
        
        # Registriere Views
        self.bot.add_view(TicketButtons())
        self.bot.add_view(TicketControlButtons())
        self.bot.add_view(ArchivedTicketButtons())
        
        # Überprüfe ob eine Ticket-Message existiert
        message_id = get_ticket_message()
        if message_id:
            channel = self.bot.get_channel(TICKET_CHANNEL_ID)
            try:
                await channel.fetch_message(message_id)
            except discord.NotFound:
                print("Ticket message not found. Please use /setup_tickets to create a new one.")
                print("Ticket message not found. Please use /setup_tickets to create a new one.")

    @app_commands.command(
        name="setup_tickets",
        description="Erstellt das Ticket-System in einem bestimmten Kanal"
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        """Sendet die Ticket-Nachricht mit Buttons"""
        try:
            if interaction.guild_id not in ALLOWED_GUILDS["tickets"]:
                await interaction.response.send_message("Sie haben keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
                return
                
            channel = self.bot.get_channel(TICKET_CHANNEL_ID)
            if not channel:
                await interaction.response.send_message("Der Ticket-Kanal wurde nicht gefunden.", ephemeral=True)
                return
            
            # Lösche alte Ticket-Message falls vorhanden
            old_message_id = get_ticket_message()
            if old_message_id:
                try:
                    old_message = await channel.fetch_message(old_message_id)
                    await old_message.delete()
                except discord.NotFound:
                    pass

            embed = discord.Embed(
                title="🎫 Ticket erstellen",
                description="Klicke auf einen der Buttons unten, um ein Ticket zu erstellen:\n\n"
                           "🛒 **Server Kauf** - Für Anfragen zum Serverkauf\n"
                           "🔧 **Technischer Support** - Bei technischen Problemen\n"
                           "❓ **Allgemeiner Support** - Für alle anderen Anfragen\n"
                           "🚫 **Entbannungsantrag** - Für Minecraft Server Entbannungsanträge",
                color=COLORS["violet"]
            )
            message = await channel.send(embed=embed, view=TicketButtons())
            save_ticket_message(message.id)
            await interaction.response.send_message("Ticket-System wurde erfolgreich eingerichtet!", ephemeral=True)
        except Exception as e:
            print(f"Fehler beim Einrichten des Ticket-Systems: {e}")
            await interaction.response.send_message("Es ist ein Fehler beim Einrichten aufgetreten.", ephemeral=True)

    @app_commands.command(
        name="ticket_info",
        description="Zeigt Informationen über ein Ticket an"
    )
    async def ticket_info(self, interaction: discord.Interaction):
        if interaction.guild_id not in ALLOWED_GUILDS["tickets"]:
            await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)
            return
        if not is_ticket(interaction.channel.id):
            await interaction.response.send_message("Dieser Befehl kann nur in einem Ticket verwendet werden!", ephemeral=True)
            return

        ticket_data = get_ticket_data(interaction.channel.id)
        if not ticket_data:
            await interaction.response.send_message("Keine Ticket-Informationen gefunden!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Ticket Informationen",
            color=COLORS["violet"]
        )
        embed.add_field(name="Ticket-Typ", value=ticket_data["Type"], inline=False)
        embed.add_field(name="Ersteller", value=f"<@{ticket_data['Owner_ID']}>", inline=False)
        embed.add_field(name="Erstellt am", value=ticket_data["Created"], inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def ticket_info_context_menu(self, interaction: discord.Interaction, message: discord.Message):
        """Context menu version of ticket_info command"""
        await self.ticket_info(interaction)

async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    try:
        await bot.add_cog(Tickets(bot))
    except Exception as e:
        print(f'Error loading {__name__}: {e}')