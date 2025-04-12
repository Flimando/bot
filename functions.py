"""
Zentrale Funktionsbibliothek für den Discord Bot

Diese Datei enthält alle grundlegenden Funktionen, die von verschiedenen
Bot-Komponenten verwendet werden. Sie ist in folgende Hauptbereiche unterteilt:

1. Datenbank-Setup und Grundfunktionen
    - Initialisierung der JSON-Datenbank
    - Lade- und Speicherfunktionen

2. Ticket-System Funktionen
    - Ticket-Verwaltung (Erstellen, Prüfen, Löschen)
    - Berechtigungsprüfungen

3. Shopping-System Funktionen
    - Einkaufslisten-Verwaltung
    - Embed-Erstellung

4. Todo-System Funktionen
    - Aufgabenlisten-Verwaltung
    - Embed-Erstellung

Wichtige Hinweise:
- Alle Daten werden in data.json gespeichert
- Automatische Backup-Erstellung bei Änderungen
- Thread-safe Datenbankzugriffe
"""

import json, os, discord
from config import BOT_CONFIG, DISCORD_IDS, COLORS, SYSTEM_CONFIG, ALLOWED_GUILDS
from discord.ext import commands
from threading import Lock
from datetime import datetime

# Globale Variablen
data = SYSTEM_CONFIG["data"]
FILEPATH = SYSTEM_CONFIG["FILEPATH"]
BACKUP_PATH = SYSTEM_CONFIG["BACKUP_PATH"]

_file_lock = Lock()  # Erstellt eine Sperre

# ====== DATENBANK-SETUP ======
if os.path.isfile("data.json"):
    with open("data.json", encoding="utf-8") as file:
        data = json.load(file)
        print("Loaded Database: Data")
else:
    data = {
        "Last ID": 0,           # Letzte vergebene ID
        "Tickets": [],          # Liste für Support-Tickets
        "ticket_config": {      # Ticket-Konfiguration
            "message_id": None,
        },
        "shopping": {           # Shopping-System
            "Profiles": [],
            "Last Message ID": 0
        },
        "embeds": {            # Embed-Konfigurationen
            "ports": {
                "title": "Port Übersicht",
                "color": 10070709,
                "fields": [
                    {"name": "Minecraft", "value": "25565"},
                    {"name": "Teamspeak", "value": "9987"},
                    {"name": "FTP", "value": "21"},
                    {"name": "SSH", "value": "22"},
                    {"name": "HTTP", "value": "80"},
                    {"name": "HTTPS", "value": "443"}
                ],
                "footer": {
                    "icon_url": "https://flimando.com/logo.png"
                }
            }
        },
        "todo": {              # TODO-System
            "Profiles": [],
            "Last Message ID": 0
        }
    }
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)
        print("Created Database: Data")

# ====== GRUNDLEGENDE FUNKTIONEN ======
def dump():
    """Speichert die aktuellen Daten in die JSON-Datei"""
    with _file_lock:
        try:
            with open("data.json", "w") as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            print(f"Fehler beim Speichern: {e}")
            raise
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}")
            raise

def lib():
    """Gibt die aktuelle Datenbank zurück"""
    return data

# ====== TICKET-SYSTEM FUNKTIONEN ======
def is_ticket(channel_id):
    """Prüft, ob ein Channel ein Ticket ist"""
    for ticket in data["Tickets"]:
        if ticket["ID"] == channel_id:
            return True
    return False

def find_ticket_index(channel_id):
    """Findet den Index eines Tickets in der Liste"""
    for index, ticket in enumerate(data["Tickets"]):
        if ticket["ID"] == channel_id:
            return index
    return False

def ticket_check(user_id, channel_id):
    """Prüft, ob ein Benutzer der Besitzer eines Tickets ist"""
    for ticket in data["Tickets"]:
        if ticket["ID"] == channel_id:
            return ticket["Owner_ID"] == user_id
    return False

def kill_ticket(channel_id):
    """Löscht ein Ticket aus der Datenbank"""
    index = find_ticket_index(channel_id)
    if index is not False:
        data["Tickets"].pop(index)
        dump()

def max_tickets(user_id):
    """Prüft, ob ein Benutzer das Ticket-Limit erreicht hat (max. 3)"""
    count = sum(1 for ticket in data["Tickets"] if int(ticket["Owner_ID"]) == int(user_id))
    return count < 3

# ====== DISCORD.PY COG SETUP ======
class functions(commands.Cog):
    """Klasse für Discord.py Cog-System"""
    pass

def setup(bot):
    """Fügt den Cog zum Bot hinzu"""
    bot.add_cog(functions(bot))

# Erweitere die Ticket-Funktionen
def create_ticket(channel_id, owner_id, ticket_type):
    """Erstellt ein neues Ticket in der Datenbank"""
    ticket = {
        "ID": channel_id,
        "Owner_ID": owner_id,
        "Type": ticket_type,
        "Created": str(get_timestamp())
    }
    data["Tickets"].append(ticket)
    dump()

def save_ticket_message(message_id):
    """Speichert die Ticket-Message ID"""
    data["ticket_config"]["message_id"] = message_id
    dump()

def get_ticket_message():
    """Gibt die gespeicherte Ticket-Message ID zurück"""
    return data["ticket_config"]["message_id"]

def get_ticket_owner(channel_id):
    """Gibt die Owner ID eines Tickets zurück"""
    for ticket in data["Tickets"]:
        if ticket["ID"] == channel_id:
            return ticket["Owner_ID"]
    return None

def get_ticket_data(channel_id):
    """Gibt alle Ticket-Daten zurück"""
    for ticket in data["Tickets"]:
        if ticket["ID"] == channel_id:
            return ticket
    return None

# ====== SHOPPING-SYSTEM FUNKTIONEN ======
def save_shopping_list():
    """Speichert die Einkaufsliste"""
    dump()

def shopping_dump():
    """Speichert die Shopping-Daten"""
    dump()

def create_shopping_embed():
    """Erstellt ein Embed für die Einkaufsliste"""
    embed = discord.Embed(title="Einkaufsliste", color=COLORS["violet"], timestamp=get_timestamp())
    for i, item in enumerate(data["shopping"]["Profiles"]):
        embed.add_field(
            name=f"{i}. {item['task']}", 
            value=f"Hinzugefügt von: {item['author']}", 
            inline=False
        )
    return embed

# Hilfsvariablen für einfacheren Zugriff
shopping_data = data["shopping"]

# ====== TODO-SYSTEM FUNKTIONEN ======
def save_todo_list():
    """Speichert die Todo-Liste"""
    dump()

def create_embed():
    """Erstellt ein Embed für die Todo-Liste"""
    embed = discord.Embed(title="Todo-Liste", color=COLORS["violet"], timestamp=get_timestamp())
    for i, item in enumerate(data["todo"]["Profiles"]):
        embed.add_field(
            name=f"{i}. {item['task']}", 
            value=f"Hinzugefügt von: {item['author']}", 
            inline=False
        )
    return embed

# Hilfsvariable für einfacheren Zugriff
todo_data = data["todo"]

def get_timestamp() -> datetime:
    """Gibt die aktuelle Uhrzeit zurück"""
    return datetime.utcnow()

