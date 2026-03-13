#!/usr/bin/env python3
"""
ServerPet 🐾 — A Tamagotchi-style virtual pet for your server.
Turn system monitoring into a fun, interactive experience!

Usage:
    python serverpet.py start [--name NAME] [--species SPECIES] [--personality PERSONALITY]
    python serverpet.py status
    python serverpet.py watch
    python serverpet.py feed
    python serverpet.py clean
    python serverpet.py play
    python serverpet.py sleep
    python serverpet.py doctor
    python serverpet.py stats
    python serverpet.py achievements
    python serverpet.py rename <name>
    python serverpet.py theme <theme>
    python serverpet.py reset
    python serverpet.py info
"""

import json
import time
import random
import socket
import argparse
from datetime import datetime
from pathlib import Path

import psutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich import box

console = Console()

# ─── Paths & Constants ──────────────────────────────────────────────────────────

STATE_DIR  = Path.home() / ".serverpet"
STATE_FILE = STATE_DIR / "state.json"
VERSION    = "1.0.0"

# ─── ASCII Art ─────────────────────────────────────────────────────────────────

ART: dict[str, dict[str, list[str]]] = {
    "cat": {
        "happy":      [" /\\_/\\ ", "( ^ω^ )", " > ♥ <  "],
        "content":    [" /\\_/\\ ", "( •ω• )", " > - <  "],
        "sad":        [" /\\_/\\ ", "( T_T )", " (   )  "],
        "angry":      [" /\\_/\\ ", "(ಠ_ಠ) ", " > ! <  "],
        "sleeping":   [" /\\_/\\ ", "(-ω- )z", " (   )  "],
        "sick":       [" /\\_/\\ ", "( x_x )", " (   )  "],
        "hungry":     [" /\\_/\\ ", "( ó_ò )", " > ~ <  "],
        "hyperactive":[" /\\_/\\ ", "(★ω★) ", " > !! < "],
        "dying":      [" /\\_/\\ ", "( ✖_✖ )", " (   )  "],
        "eating":     [" /\\_/\\ ", "(≧▽≦) ", " >nom<  "],
        "playing":    [" /\\_/\\ ", "(≧ω≦) ", " >yay<  "],
        "dizzy":      [" /\\_/\\ ", "( @_@ )", " > ? <  "],
        "sluggish":   [" /\\_/\\ ", "( -_- )", " > … <  "],
    },
    "robot": {
        "happy":      [" [^‿^] ", " | ♥ | ", " |___| "],
        "content":    [" [•_•] ", " |   | ", " |___| "],
        "sad":        [" [;_;] ", " | ↓ | ", " |___| "],
        "angry":      [" [>_<] ", " | ! | ", " |___| "],
        "sleeping":   [" [-_-] ", " |zzz| ", " |___| "],
        "sick":       [" [x_x] ", " |ERR| ", " |___| "],
        "hungry":     [" [o_O] ", " |LOW| ", " |___| "],
        "hyperactive":[" [★_★] ", " |MAX| ", " |___| "],
        "dying":      [" [✖_✖] ", " |SOS| ", " |___| "],
        "eating":     [" [^ω^] ", " |PWR| ", " |___| "],
        "playing":    [" [^_^] ", " |FUN| ", " |___| "],
        "dizzy":      [" [@_@] ", " |???| ", " |___| "],
        "sluggish":   [" [~_~] ", " |LAG| ", " |___| "],
    },
    "blob": {
        "happy":      ["  ___  ", " (^‿^) ", "  \\_/  "],
        "content":    ["  ___  ", " (•_•) ", "  \\_/  "],
        "sad":        ["  ___  ", " (T_T) ", "  \\_/  "],
        "angry":      ["  ___  ", "(ಠ_ಠ) ", "  \\_/  "],
        "sleeping":   ["  ___  ", "(-_-)z ", "  \\_/  "],
        "sick":       ["  ___  ", " (x_x) ", "  \\_/  "],
        "hungry":     ["  ___  ", " (ó_ò) ", "  \\_/  "],
        "hyperactive":["  ___  ", " (★_★) ", "  \\_/  "],
        "dying":      ["  ___  ", " (✖_✖) ", "  \\_/  "],
        "eating":     ["  ___  ", "(≧▽≦) ", "  \\_/  "],
        "playing":    ["  ___  ", "(≧ω≦) ", "  \\_/  "],
        "dizzy":      ["  ___  ", " (@_@) ", "  \\_/  "],
        "sluggish":   ["  ___  ", " (-_-) ", "  \\_/  "],
    },
    "alien": {
        "happy":      ["  /^\\  ", " (^‿^) ", "  ) (  "],
        "content":    ["  /^\\  ", " (•_•) ", "  ) (  "],
        "sad":        ["  /^\\  ", " (T_T) ", "  ) (  "],
        "angry":      ["  /^\\  ", "(ಠ_ಠ) ", "  ) (  "],
        "sleeping":   ["  /^\\  ", "(-_-)z ", "  ) (  "],
        "sick":       ["  /^\\  ", " (x_x) ", "  ) (  "],
        "hungry":     ["  /^\\  ", " (ó_ò) ", "  ) (  "],
        "hyperactive":["  /^\\  ", " (★_★) ", "  ) (  "],
        "dying":      ["  /^\\  ", " (✖_✖) ", "  ) (  "],
        "eating":     ["  /^\\  ", "(≧▽≦) ", "  ) (  "],
        "playing":    ["  /^\\  ", "(≧ω≦) ", "  ) (  "],
        "dizzy":      ["  /^\\  ", " (@_@) ", "  ) (  "],
        "sluggish":   ["  /^\\  ", " (-_-) ", "  ) (  "],
    },
    "dragon": {
        "happy":      [" <<^>> ", " (^‿^) ", "/|   |\\ "],
        "content":    [" <<^>> ", " (•_•) ", "/|   |\\ "],
        "sad":        [" <<^>> ", " (T_T) ", "/|   |\\ "],
        "angry":      [" <<^>> ", "(ಠ_ಠ) ", "/|   |\\ "],
        "sleeping":   [" <<^>> ", "(-_-)z ", "/|   |\\ "],
        "sick":       [" <<^>> ", " (x_x) ", "/|   |\\ "],
        "hungry":     [" <<^>> ", " (ó_ò) ", "/|   |\\ "],
        "hyperactive":[" <<^>> ", " (★_★) ", "/|   |\\ "],
        "dying":      [" <<^>> ", " (✖_✖) ", "/|   |\\ "],
        "eating":     [" <<^>> ", "(≧▽≦) ", "/|   |\\ "],
        "playing":    [" <<^>> ", "(≧ω≦) ", "/|   |\\ "],
        "dizzy":      [" <<^>> ", " (@_@) ", "/|   |\\ "],
        "sluggish":   [" <<^>> ", " (-_-) ", "/|   |\\ "],
    },
}

SPECIES       = list(ART.keys())
PERSONALITIES = ["lazy", "energetic", "dramatic", "grumpy", "cheerful", "stoic"]

# ─── Color Themes ──────────────────────────────────────────────────────────────

THEMES: dict[str, dict] = {
    "default": {"primary": "cyan",    "secondary": "green",       "warning": "yellow", "danger": "red",    "pet": "bright_cyan"},
    "matrix":  {"primary": "green",   "secondary": "bright_green","warning": "yellow", "danger": "red",    "pet": "bright_green"},
    "sunset":  {"primary": "magenta", "secondary": "yellow",      "warning": "orange1","danger": "red",    "pet": "bright_magenta"},
    "ocean":   {"primary": "blue",    "secondary": "cyan",        "warning": "yellow", "danger": "red",    "pet": "bright_blue"},
    "hacker":  {"primary": "bright_green","secondary": "green",   "warning": "yellow", "danger": "red",    "pet": "bold bright_green"},
}

# ─── Achievements ──────────────────────────────────────────────────────────────

ACHIEVEMENTS = {
    "server_whisperer": {"name": "Server Whisperer",  "icon": "🏆", "desc": "System uptime above 30 days"},
    "pet_doctor":       {"name": "Pet Doctor",         "icon": "💊", "desc": "Healed the pet 10 times"},
    "clean_server":     {"name": "Clean Server",       "icon": "✨", "desc": "Disk usage under 40% for 7 days"},
    "happy_streak":     {"name": "Joy Machine",        "icon": "😊", "desc": "Pet happy for 24 hours straight"},
    "night_owl":        {"name": "Night Owl",          "icon": "🦉", "desc": "Checked on the pet at midnight"},
    "gamer":            {"name": "Gamer",              "icon": "🎮", "desc": "Won 10 mini-games"},
    "survivor":         {"name": "Survivor",           "icon": "💪", "desc": "Pet survived a critical health event"},
    "old_friend":       {"name": "Old Friend",         "icon": "🌟", "desc": "Pet is 30 days old"},
}

# ─── Default State ─────────────────────────────────────────────────────────────

DEFAULT_STATE: dict = {
    "name": "Byte",
    "species": "cat",
    "personality": "cheerful",
    "theme": "default",
    "health": 100.0,
    "hunger": 0.0,
    "energy": 100.0,
    "happiness": 100.0,
    "cleanliness": 100.0,
    "age_days": 0.0,
    "created_at": None,
    "last_updated": None,
    "last_fed": None,
    "last_cleaned": None,
    "last_played": None,
    "mood": "happy",
    "alive": True,
    "death_cause": None,
    "achievements": {},
    "counters": {
        "heals": 0,
        "clean_days": 0.0,
        "happy_hours": 0.0,
        "midnight_checks": 0,
        "games_won": 0,
        "survived_critical": False,
    },
}

# ─── Persistence ───────────────────────────────────────────────────────────────

def load_state() -> dict | None:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return None


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def get_state() -> dict:
    s = load_state()
    if s is None:
        s = DEFAULT_STATE.copy()
        s["counters"] = DEFAULT_STATE["counters"].copy()
        s["achievements"] = {}
        s["created_at"] = datetime.now().isoformat()
        save_state(s)
    for k, v in DEFAULT_STATE.items():
        if k not in s:
            s[k] = v
    if "counters" not in s:
        s["counters"] = DEFAULT_STATE["counters"].copy()
    return s


# ─── System Metrics ────────────────────────────────────────────────────────────

def get_metrics() -> dict:
    m: dict = {}

    m["cpu"] = psutil.cpu_percent(interval=0.3)

    mem = psutil.virtual_memory()
    m["ram"]          = mem.percent
    m["ram_used_gb"]  = round(mem.used  / 1024**3, 2)
    m["ram_total_gb"] = round(mem.total / 1024**3, 2)

    try:
        disk = psutil.disk_usage("/")
        m["disk"]         = disk.percent
        m["disk_free_gb"] = round(disk.free  / 1024**3, 2)
        m["disk_total_gb"]= round(disk.total / 1024**3, 2)
    except Exception:
        m["disk"] = m["disk_free_gb"] = m["disk_total_gb"] = 0

    try:
        net = psutil.net_io_counters()
        m["net_sent"] = net.bytes_sent
        m["net_recv"] = net.bytes_recv
    except Exception:
        m["net_sent"] = m["net_recv"] = 0

    # ── Network latency via socket connect ──────────────────────────────
    try:
        _t = time.time()
        _sock = socket.create_connection(("8.8.8.8", 53), timeout=1)
        _sock.close()
        m["net_latency"] = round((time.time() - _t) * 1000, 1)
    except Exception:
        m["net_latency"] = None

    # ── Packet loss via dropin/dropout delta ────────────────────────────
    try:
        _n1 = psutil.net_io_counters()
        time.sleep(0.05)
        _n2 = psutil.net_io_counters()
        _drop  = max(0, (_n2.dropin  - _n1.dropin) + (_n2.dropout - _n1.dropout))
        _total = max(0, (_n2.packets_recv - _n1.packets_recv) + (_n2.packets_sent - _n1.packets_sent)) + _drop
        m["packet_loss_pct"] = round((_drop / _total) * 100, 1) if _total > 0 else 0.0
    except Exception:
        m["packet_loss_pct"] = 0.0

    m["procs"]       = len(psutil.pids())
    uptime_s         = time.time() - psutil.boot_time()
    m["uptime_s"]    = uptime_s
    m["uptime_days"] = uptime_s / 86400
    m["uptime_str"]  = _fmt_uptime(uptime_s)

    try:
        temps = psutil.sensors_temperatures()
        if temps:
            vals = [t.current for ts in temps.values() for t in ts if t.current > 0]
            m["temp"] = round(sum(vals)/len(vals), 1) if vals else None
        else:
            m["temp"] = None
    except Exception:
        m["temp"] = None

    return m


def _fmt_uptime(s: float) -> str:
    d, s = divmod(int(s), 86400)
    h, s = divmod(s, 3600)
    mi    = s // 60
    if d:  return f"{d}d {h}h {mi}m"
    if h:  return f"{h}h {mi}m"
    return f"{mi}m"


# ─── Pet Logic ─────────────────────────────────────────────────────────────────

def _determine_mood(s: dict, m: dict) -> str:
    if not s["alive"]:
        return "dying"
    h, hunger, energy, happy, clean = (
        s["health"], s["hunger"], s["energy"], s["happiness"], s["cleanliness"]
    )
    cpu  = m.get("cpu",  0)
    ram  = m.get("ram",  0)
    disk = m.get("disk", 0)
    packet_loss = m.get("packet_loss_pct", 0)
    latency     = m.get("net_latency")
    p = s.get("personality", "cheerful")

    if h < 15:      return "dying"
    if h < 35:      return "sick"
    if energy < 20: return "sleeping"
    if hunger > 80: return "hungry"

    if cpu > 90 or ram > 90:
        return "dying" if p == "dramatic" else "angry"

    if cpu > 65 and p == "energetic":
        return "hyperactive"

    # Network-based moods
    if packet_loss > 10:
        return "dizzy"
    if latency is not None and latency > 200:
        return "sluggish"

    if happy < 30 or clean < 20:
        return "sad"

    if happy > 80 and h > 80:
        return "happy"

    return "content"


def update_state(s: dict, m: dict) -> dict:
    now = datetime.now()
    try:
        last    = datetime.fromisoformat(s["last_updated"])
        elapsed = min((now - last).total_seconds() / 60, 120)
    except Exception:
        elapsed = 1.0

    p    = s.get("personality", "cheerful")
    cpu  = m.get("cpu",  0)
    ram  = m.get("ram",  0)
    disk = m.get("disk", 0)

    # ── Hunger ──────────────────
    hr = 0.10 + (0.30 if disk > 90 else 0.10 if disk > 75 else 0)
    if p == "lazy":         hr *= 0.7
    elif p == "energetic":  hr *= 1.4
    s["hunger"] = min(100, s["hunger"] + hr * elapsed)

    # ── Energy ──────────────────
    er = 0.15 + (0.30 if cpu > 80 else 0.10 if cpu > 60 else 0)
    if p == "lazy":         er *= 1.4
    elif p == "energetic":  er *= 0.7
    s["energy"] = max(0, s["energy"] - er * elapsed)

    # ── Cleanliness ─────────────
    cr = 0.08 + (0.10 if ram > 85 else 0)
    s["cleanliness"] = max(0, s["cleanliness"] - cr * elapsed)

    # ── Health ──────────────────
    dh = 0.0
    if cpu  > 90: dh -= 0.25
    if ram  > 90: dh -= 0.20
    if disk > 95: dh -= 0.30
    if s["hunger"]      > 85: dh -= 0.20
    if s["cleanliness"] < 20: dh -= 0.10
    if cpu < 50 and ram < 60 and disk < 75 and s["hunger"] < 50:
        dh += 0.06

    was_critical = s["health"] < 25
    s["health"] = max(0, min(100, s["health"] + dh * elapsed))
    if was_critical and s["health"] >= 50:
        s["counters"]["survived_critical"] = True

    # ── Happiness ───────────────
    dh2 = 0.0
    if cpu < 40 and ram < 50:       dh2 += 0.10
    if s["hunger"]      > 70:       dh2 -= 0.20
    if s["cleanliness"] < 30:       dh2 -= 0.15
    if s["energy"]      < 30:       dh2 -= 0.10
    if m.get("packet_loss_pct", 0) > 10: dh2 -= 0.10   # packet loss makes pet sad
    if p == "grumpy":               dh2 -= 0.05
    elif p == "cheerful":           dh2 += 0.05
    s["happiness"] = max(0, min(100, s["happiness"] + dh2 * elapsed))

    # ── Age ─────────────────────
    try:
        created   = datetime.fromisoformat(s["created_at"])
        s["age_days"] = (now - created).total_seconds() / 86400
    except Exception:
        pass

    # ── Death ───────────────────
    if s["health"] <= 0:
        s["alive"] = False
        if   cpu  > 90: s["death_cause"] = "CPU overload"
        elif ram  > 90: s["death_cause"] = "RAM exhaustion"
        elif disk > 95: s["death_cause"] = "Disk full"
        else:           s["death_cause"] = "Neglect"

    s["mood"] = _determine_mood(s, m)

    # ── Achievement counters ─────
    c = s["counters"]
    if s["mood"] == "happy":
        c["happy_hours"] = c.get("happy_hours", 0) + elapsed / 60
    if disk < 40:
        c["clean_days"]  = c.get("clean_days",  0) + elapsed / 1440
    if now.hour == 0:
        c["midnight_checks"] = c.get("midnight_checks", 0) + 1

    # ── Unlock achievements ──────
    ach = s["achievements"]
    if m.get("uptime_days", 0) >= 30 and "server_whisperer" not in ach:
        ach["server_whisperer"] = now.isoformat()
    if c.get("heals", 0) >= 10 and "pet_doctor" not in ach:
        ach["pet_doctor"] = now.isoformat()
    if c.get("clean_days", 0) >= 7 and "clean_server" not in ach:
        ach["clean_server"] = now.isoformat()
    if c.get("happy_hours", 0) >= 24 and "happy_streak" not in ach:
        ach["happy_streak"] = now.isoformat()
    if c.get("midnight_checks", 0) >= 1 and "night_owl" not in ach:
        ach["night_owl"] = now.isoformat()
    if c.get("games_won", 0) >= 10 and "gamer" not in ach:
        ach["gamer"] = now.isoformat()
    if c.get("survived_critical") and "survivor" not in ach:
        ach["survivor"] = now.isoformat()
    if s["age_days"] >= 30 and "old_friend" not in ach:
        ach["old_friend"] = now.isoformat()

    return s


# ─── Display Helpers ───────────────────────────────────────────────────────────

def theme(s: dict) -> dict:
    return THEMES.get(s.get("theme", "default"), THEMES["default"])


def pet_art(s: dict, override_mood: str | None = None) -> list[str]:
    sp   = s.get("species", "cat")
    mood = override_mood or s.get("mood", "content")
    species_art = ART.get(sp, ART["cat"])
    return species_art.get(mood, species_art.get("content", ["       ", "(•_•)  ", "       "]))


def mood_icon(mood: str) -> str:
    return {
        "happy":      "😊",
        "content":    "😌",
        "sad":        "😢",
        "angry":      "😠",
        "sleeping":   "😴",
        "sick":       "🤒",
        "hungry":     "😋",
        "hyperactive":"⚡",
        "dying":      "💀",
        "eating":     "😋",
        "playing":    "🎮",
        "dizzy":      "😵",
        "sluggish":   "🐌",
    }.get(mood, "😐")


def mood_color(mood: str, th: dict) -> str:
    return {
        "happy":      th["secondary"],
        "content":    th["primary"],
        "sad":        "blue",
        "angry":      th["danger"],
        "sleeping":   "dim white",
        "sick":       th["danger"],
        "hungry":     th["warning"],
        "hyperactive":"bright_yellow",
        "dying":      "bright_red",
        "dizzy":      th["warning"],
        "sluggish":   "dim cyan",
    }.get(mood, th["primary"])


def stat_bar(val: float, th: dict, width: int = 16) -> Text:
    filled = max(0, min(width, int((val / 100) * width)))
    bar    = "█" * filled + "░" * (width - filled)
    color  = th["secondary"] if val > 65 else th["warning"] if val > 35 else th["danger"]
    t = Text()
    t.append(f"[{bar}] ", style=color)
    t.append(f"{val:5.1f}%", style="bold " + color)
    return t


def _reaction(personality: str, event: str) -> str:
    table = {
        "dramatic": {
            "fed":    "OH! SUSTENANCE! I WAS ON THE BRINK OF OBLIVION! 🎭",
            "cleaned":"FINALLY! I was drowning in filth! The drama is over! 🎭",
            "played": "THIS IS THE GREATEST DAY OF MY ENTIRE EXISTENCE! 🎭",
            "healed": "I HAVE BEEN GIVEN ANOTHER CHANCE AT LIFE! 🎭",
        },
        "lazy": {
            "fed":    "Mm... food... *yawn*... thanks...",
            "cleaned":"Whatever... at least it's cleaner now...",
            "played": "Okay, I played a little... can I nap now?",
            "healed": "Oh... I guess I feel better... *goes back to sleep*",
        },
        "grumpy": {
            "fed":    "About time! I was starving, you know!",
            "cleaned":"It's STILL not clean enough, but it'll do.",
            "played": "That was barely adequate. Hmph.",
            "healed": "Took you long enough to fix things.",
        },
        "energetic": {
            "fed":    "FUEL ACQUIRED! LET'S GO! 🚀",
            "cleaned":"SPARKLING CLEAN! NOW LET'S MOVE! 🚀",
            "played": "YES! MORE! AGAIN! AGAIN! 🚀",
            "healed": "BACK IN ACTION! AT 110%! 🚀",
        },
        "cheerful": {
            "fed":    "Yay! Thank you for the food! 🌟",
            "cleaned":"Everything is shiny and wonderful! ✨",
            "played": "That was so much fun! You're the best! 🌟",
            "healed": "Feeling better already! Thanks! 💖",
        },
        "stoic": {
            "fed":    "Nutritional requirements met.",
            "cleaned":"Hygiene restored to acceptable levels.",
            "played": "Recreation protocols executed.",
            "healed": "Operational status: nominal.",
        },
    }
    defaults = {"fed": "Nom nom nom! 🍖", "cleaned": "Squeaky clean! ✨",
                "played": "Wheee! 🎉",   "healed": "Feeling better! 💊"}
    return table.get(personality, defaults).get(event, defaults.get(event, "..."))


# ─── Commands ──────────────────────────────────────────────────────────────────

def cmd_start(args) -> None:
    existing = load_state()
    if existing and existing.get("alive", True) and not getattr(args, "reset", False):
        console.print(Panel(
            f"[yellow]A pet named [bold]{existing['name']}[/bold] already exists![/yellow]\n\n"
            f"Use [cyan]serverpet status[/cyan] to check on them, or\n"
            f"[red]serverpet start --reset[/red] to start fresh.",
            title="🐾 ServerPet", border_style="yellow",
        ))
        return

    if getattr(args, "reset", False) and STATE_FILE.exists():
        STATE_FILE.unlink()

    name        = getattr(args, "name", "Byte")       or "Byte"
    species     = getattr(args, "species", "cat")     or "cat"
    personality = getattr(args, "personality", None)  or random.choice(PERSONALITIES)

    if species not in ART:
        console.print(f"[red]Unknown species. Choose: {', '.join(SPECIES)}[/red]")
        return

    s = DEFAULT_STATE.copy()
    s["counters"]    = DEFAULT_STATE["counters"].copy()
    s["achievements"]= {}
    s["name"]        = name
    s["species"]     = species
    s["personality"] = personality
    s["created_at"]  = datetime.now().isoformat()
    save_state(s)

    th  = theme(s)
    art = "\n".join(f"  {l}" for l in pet_art(s, "happy"))

    console.print(Panel(
        f"[{th['pet']}]{art}[/{th['pet']}]\n\n"
        f"🎉 Welcome, [bold]{name}[/bold]!\n"
        f"   Species:     [cyan]{species.title()}[/cyan]\n"
        f"   Personality: [magenta]{personality.title()}[/magenta]\n\n"
        f"Keep them healthy:\n"
        f"  • [cyan]serverpet watch[/cyan]   — live dashboard\n"
        f"  • [cyan]serverpet feed[/cyan]    — when hungry\n"
        f"  • [cyan]serverpet play[/cyan]    — when bored\n"
        f"  • [cyan]serverpet doctor[/cyan]  — when sick\n"
        f"  • [cyan]serverpet info[/cyan]    — all commands",
        title="🐾 ServerPet — New Pet!", border_style=th["primary"],
    ))


def cmd_status(args=None) -> None:
    s  = get_state()
    m  = get_metrics()
    s  = update_state(s, m)
    save_state(s)

    th   = theme(s)
    mood = s["mood"]
    mc   = mood_color(mood, th)
    art  = "\n".join(f"  {l}" for l in pet_art(s))

    pet_tbl = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    pet_tbl.add_column("K", style="bold white")
    pet_tbl.add_column("V")

    pet_tbl.add_row("Mood",        Text(f"{mood_icon(mood)} {mood.title()}", style=mc))
    pet_tbl.add_row("Health",      stat_bar(s["health"],       th))
    pet_tbl.add_row("Hunger",      stat_bar(100 - s["hunger"], th))
    pet_tbl.add_row("Energy",      stat_bar(s["energy"],       th))
    pet_tbl.add_row("Happiness",   stat_bar(s["happiness"],    th))
    pet_tbl.add_row("Cleanliness", stat_bar(s["cleanliness"],  th))
    pet_tbl.add_row("Age",         Text(f"{s['age_days']:.1f} days", style=th["primary"]))

    sys_tbl = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    sys_tbl.add_column("K", style="bold white")
    sys_tbl.add_column("V")

    def inv_bar(val): return stat_bar(100 - val, th)

    sys_tbl.add_row("CPU",       inv_bar(m["cpu"]))
    sys_tbl.add_row("RAM",       inv_bar(m["ram"]))
    sys_tbl.add_row("Disk",      inv_bar(m["disk"]))
    sys_tbl.add_row("Processes", Text(str(m["procs"]), style=th["primary"]))
    sys_tbl.add_row("Uptime",    Text(m["uptime_str"], style=th["secondary"]))

    # Network stats
    lat = m.get("net_latency")
    ploss = m.get("packet_loss_pct", 0)
    lat_str   = f"{lat}ms" if lat is not None else "unreachable"
    lat_color = th["danger"] if lat is None else th["danger"] if lat > 200 else th["warning"] if lat > 100 else th["secondary"]
    ploss_color = th["danger"] if ploss > 10 else th["warning"] if ploss > 2 else th["secondary"]
    sys_tbl.add_row("Latency",     Text(lat_str,        style=lat_color))
    sys_tbl.add_row("Packet Loss", Text(f"{ploss:.1f}%", style=ploss_color))

    if m.get("temp"):
        tc = th["danger"] if m["temp"] > 80 else th["warning"] if m["temp"] > 60 else th["secondary"]
        sys_tbl.add_row("Temp", Text(f"{m['temp']}°C", style=tc))

    title  = (
        f"💀 {s['name']} passed away — {s.get('death_cause','?')}"
        if not s["alive"]
        else f"🐾 {s['name']} the {s['species'].title()} [{s['personality'].title()}]"
    )
    border = "red" if not s["alive"] else th["primary"]

    console.print(Panel(f"[{th['pet']}]{art}[/{th['pet']}]", title=title, border_style=border))
    console.print(Panel(pet_tbl, title="Pet Status",   border_style=th["secondary"]))
    console.print(Panel(sys_tbl, title="System Stats", border_style=th.get("info", th["primary"])))

    if s.get("achievements"):
        lines = []
        for k, _ in s["achievements"].items():
            if k in ACHIEVEMENTS:
                a = ACHIEVEMENTS[k]
                lines.append(f"  {a['icon']} [bold]{a['name']}[/bold]: {a['desc']}")
        if lines:
            console.print(Panel("\n".join(lines), title="🏆 Achievements", border_style="gold1"))


def cmd_feed(args=None) -> None:
    s = get_state()
    if not s["alive"]:
        console.print("[red]Your pet has passed away.[/red]"); return

    m  = get_metrics()
    s  = update_state(s, m)
    th = theme(s)

    before = s["hunger"]
    s["hunger"]    = max(0,   s["hunger"]    - 40)
    s["happiness"] = min(100, s["happiness"] + 10)
    s["health"]    = min(100, s["health"]    +  5)
    s["last_fed"]  = datetime.now().isoformat()

    art = "\n".join(f"  {l}" for l in pet_art(s, "eating"))
    r   = _reaction(s.get("personality","cheerful"), "fed")

    console.print(Panel(
        f"[{th['pet']}]{art}[/{th['pet']}]\n\n"
        f"[bold green]🍖 Nom nom nom![/bold green]\n"
        f"Hunger: {before:.0f}% → {s['hunger']:.0f}%\n\n"
        f"[italic]{s['name']} says: \"{r}\"[/italic]",
        title=f"🍖 Feeding {s['name']}", border_style="green",
    ))
    s["mood"] = _determine_mood(s, m)
    save_state(s)


def cmd_clean(args=None) -> None:
    s = get_state()
    if not s["alive"]:
        console.print("[red]Your pet has passed away.[/red]"); return

    m  = get_metrics()
    s  = update_state(s, m)
    th = theme(s)

    before = s["cleanliness"]
    s["cleanliness"] = min(100, s["cleanliness"] + 50)
    s["happiness"]   = min(100, s["happiness"]   +  5)
    s["last_cleaned"]= datetime.now().isoformat()

    art = "\n".join(f"  {l}" for l in pet_art(s))
    r   = _reaction(s.get("personality","cheerful"), "cleaned")

    console.print(Panel(
        f"[{th['pet']}]{art}[/{th['pet']}]\n\n"
        f"[bold cyan]✨ Squeaky clean![/bold cyan]\n"
        f"Cleanliness: {before:.0f}% → {s['cleanliness']:.0f}%\n\n"
        f"[italic]{s['name']} says: \"{r}\"[/italic]",
        title=f"✨ Cleaning {s['name']}", border_style="cyan",
    ))
    s["mood"] = _determine_mood(s, m)
    save_state(s)


def cmd_play(args=None) -> None:
    s = get_state()
    if not s["alive"]:
        console.print("[red]Your pet has passed away.[/red]"); return

    m  = get_metrics()
    s  = update_state(s, m)
    th = theme(s)

    if s["energy"] < 20:
        console.print(f"[yellow]{s['name']} is too tired to play! Try 'serverpet sleep' first.[/yellow]")
        return

    secret   = random.randint(1, 10)
    attempts = 3
    won      = False

    console.print(Panel(
        "🎮 [bold]Guess the Number[/bold]\n\nGuess a number between [cyan]1[/cyan] and [cyan]10[/cyan]!",
        title="Mini-Game", border_style="magenta",
    ))

    for i in range(attempts):
        try:
            raw   = input(f"  Attempt {i+1}/{attempts}: ")
            guess = int(raw.strip())
        except (ValueError, EOFError):
            console.print("  [red]Invalid input — skipping.[/red]")
            continue

        if guess == secret:
            won = True
            break
        hint = "[yellow]Too low! ↑[/yellow]" if guess < secret else "[yellow]Too high! ↓[/yellow]"
        console.print(f"  {hint}")

    p = s.get("personality","cheerful")
    if won:
        s["happiness"] = min(100, s["happiness"] + 25)
        s["counters"]["games_won"] = s["counters"].get("games_won", 0) + 1
        if s["counters"]["games_won"] >= 10 and "gamer" not in s["achievements"]:
            s["achievements"]["gamer"] = datetime.now().isoformat()
            console.print("[gold1]🏆 Achievement Unlocked: Gamer![/gold1]")
        r = _reaction(p, "played")
        console.print(Panel(
            f"🎉 [bold green]You got it![/bold green] The number was [bold]{secret}[/bold]!\n\n"
            f"[italic]{s['name']} says: \"{r}\"[/italic]\n"
            f"Happiness [green]+25[/green]",
            title="🎮 You Won!", border_style="green",
        ))
    else:
        s["happiness"] = min(100, s["happiness"] + 5)
        console.print(Panel(
            f"[yellow]Better luck next time![/yellow] The number was [bold]{secret}[/bold].\n"
            f"Happiness [yellow]+5[/yellow] (for trying!)",
            title="🎮 Game Over", border_style="yellow",
        ))

    s["energy"]     = max(0, s["energy"] - 10)
    s["last_played"]= datetime.now().isoformat()
    s["mood"] = _determine_mood(s, m)
    save_state(s)


def cmd_sleep(args=None) -> None:
    s = get_state()
    if not s["alive"]:
        console.print("[red]Your pet has passed away.[/red]"); return

    m  = get_metrics()
    s  = update_state(s, m)
    th = theme(s)

    hours  = getattr(args, "duration", 8) or 8
    before = s["energy"]
    s["energy"] = min(100, s["energy"] + hours * 5)

    art = "\n".join(f"  {l}" for l in pet_art(s, "sleeping"))
    console.print(Panel(
        f"[{th['pet']}]{art}[/{th['pet']}]\n\n"
        f"[dim]💤 {s['name']} is resting... ({hours}h simulated)[/dim]\n"
        f"Energy: {before:.0f}% → {s['energy']:.0f}%",
        title=f"💤 {s['name']} Sleeping", border_style="dim white",
    ))
    s["mood"] = _determine_mood(s, m)
    save_state(s)


def cmd_doctor(args=None) -> None:
    s = get_state()
    if not s["alive"]:
        console.print("[red]Your pet has passed away. Use 'serverpet start --reset' for a new one.[/red]")
        return

    m  = get_metrics()
    s  = update_state(s, m)
    th = theme(s)

    if s["health"] > 90:
        console.print(f"[green]{s['name']} is already very healthy ({s['health']:.0f}%)![/green]")
        return

    before = s["health"]
    s["health"]  = min(100, s["health"]  + 35)
    s["hunger"]  = max(0,   s["hunger"]  - 20)
    s["counters"]["heals"] = s["counters"].get("heals", 0) + 1

    if s["counters"]["heals"] >= 10 and "pet_doctor" not in s["achievements"]:
        s["achievements"]["pet_doctor"] = datetime.now().isoformat()
        console.print("[gold1]🏆 Achievement Unlocked: Pet Doctor![/gold1]")

    art = "\n".join(f"  {l}" for l in pet_art(s))
    r   = _reaction(s.get("personality","cheerful"), "healed")

    console.print(Panel(
        f"[{th['pet']}]{art}[/{th['pet']}]\n\n"
        f"[bold green]💊 Medical treatment applied![/bold green]\n"
        f"Health: {before:.0f}% → {s['health']:.0f}%\n\n"
        f"[italic]{s['name']} says: \"{r}\"[/italic]",
        title=f"💊 Doctor Visit — {s['name']}", border_style="green",
    ))
    s["mood"] = _determine_mood(s, m)
    save_state(s)


def cmd_stats(args=None) -> None:
    s  = get_state()
    m  = get_metrics()
    th = theme(s)

    def si(val, warn=70, danger=85):
        if val > danger: return "[red]🔴 Critical[/red]"
        if val > warn:   return "[yellow]🟡 Warning[/yellow]"
        return "[green]🟢 Good[/green]"

    tbl = Table(title="📊 System Statistics", box=box.ROUNDED, border_style=th["primary"])
    tbl.add_column("Metric",  style="bold")
    tbl.add_column("Value",   justify="right")
    tbl.add_column("Status",  justify="center")

    tbl.add_row("CPU Usage",  f"{m['cpu']:.1f}%",                                    si(m["cpu"]))
    tbl.add_row("RAM Usage",  f"{m['ram']:.1f}% ({m['ram_used_gb']}GB / {m['ram_total_gb']}GB)", si(m["ram"]))
    tbl.add_row("Disk Usage", f"{m['disk']:.1f}% ({m['disk_free_gb']}GB free)",       si(m["disk"]))
    tbl.add_row("Processes",  str(m["procs"]),                                        "ℹ️  Info")
    tbl.add_row("Uptime",     m["uptime_str"],                                        "[green]🟢 Running[/green]")

    lat   = m.get("net_latency")
    ploss = m.get("packet_loss_pct", 0)
    lat_str    = f"{lat}ms" if lat is not None else "unreachable"
    lat_status = "[red]🔴 Unreachable[/red]" if lat is None else si(lat, warn=100, danger=200)
    tbl.add_row("Net Latency",    lat_str,           lat_status)
    tbl.add_row("Packet Loss",    f"{ploss:.1f}%",   si(ploss, warn=2, danger=10))

    if m.get("temp"):
        tbl.add_row("Temperature", f"{m['temp']}°C", si(m["temp"], 60, 80))

    console.print(tbl)
    console.print(Panel(
        f"[bold]How system health maps to {s['name']}:[/bold]\n\n"
        f"  CPU > 90%         → {s['name']} gets [red]angry[/red] / stressed\n"
        f"  RAM > 90%         → {s['name']} gets [yellow]tired[/yellow]\n"
        f"  Disk > 90%        → {s['name']} gets [yellow]hungry[/yellow]\n"
        f"  Packet loss > 10% → {s['name']} gets [yellow]dizzy[/yellow] 😵\n"
        f"  Latency > 200ms   → {s['name']} gets [cyan]sluggish[/cyan] 🐌\n"
        f"  All OK            → {s['name']} stays [green]happy[/green] 😊",
        title="Metric ↔ Pet Mapping", border_style=th["secondary"],
    ))


def cmd_achievements(args=None) -> None:
    s  = get_state()
    th = theme(s)

    tbl = Table(title="🏆 Achievements", box=box.ROUNDED, border_style="gold1")
    tbl.add_column("Achievement", style="bold")
    tbl.add_column("Description")
    tbl.add_column("Status",   justify="center")
    tbl.add_column("Unlocked", justify="center")

    for key, a in ACHIEVEMENTS.items():
        unlocked = key in s.get("achievements", {})
        status   = "[green]✅ Unlocked[/green]" if unlocked else "[dim]🔒 Locked[/dim]"
        date_str = ""
        if unlocked:
            try:
                date_str = datetime.fromisoformat(s["achievements"][key]).strftime("%Y-%m-%d")
            except Exception:
                date_str = "?"
        tbl.add_row(f"{a['icon']} {a['name']}", a["desc"], status, date_str)

    console.print(tbl)
    total    = len(ACHIEVEMENTS)
    unlocked = len(s.get("achievements", {}))
    console.print(f"\n[{th['secondary']}]Progress: {unlocked}/{total} achievements unlocked[/{th['secondary']}]")


def cmd_rename(args) -> None:
    s = get_state()
    old, s["name"] = s["name"], args.name
    save_state(s)
    console.print(f"[green]Renamed {old} → {s['name']}![/green]")


def cmd_theme(args) -> None:
    s = get_state()
    if args.theme not in THEMES:
        console.print(f"[red]Unknown theme. Choose: {', '.join(THEMES)}[/red]"); return
    s["theme"] = args.theme
    save_state(s)
    console.print(f"[green]Theme changed to '{args.theme}'![/green]")


def cmd_reset(args=None) -> None:
    confirm = input("⚠️  This deletes your pet! Type 'yes' to confirm: ")
    if confirm.strip().lower() == "yes":
        STATE_FILE.unlink(missing_ok=True)
        console.print("[green]Pet deleted. Run 'serverpet start' to begin again.[/green]")
    else:
        console.print("[yellow]Reset cancelled.[/yellow]")


def cmd_info(args=None) -> None:
    console.print(Panel(
        f"[bold cyan]ServerPet v{VERSION}[/bold cyan] 🐾\n"
        f"[italic]A Tamagotchi-style virtual pet for your server![/italic]\n\n"
        f"[bold]Species:[/bold]      {', '.join(SPECIES)}\n"
        f"[bold]Personalities:[/bold]{', '.join(PERSONALITIES)}\n"
        f"[bold]Themes:[/bold]       {', '.join(THEMES)}\n"
        f"[bold]State file:[/bold]   {STATE_FILE}\n\n"
        f"[bold underline]Commands[/bold underline]\n"
        f"  [cyan]start[/cyan]         Create a new pet  [dim]--name --species --personality --reset[/dim]\n"
        f"  [cyan]status[/cyan]        View pet & system at a glance\n"
        f"  [cyan]watch[/cyan]         Live auto-refreshing dashboard\n"
        f"  [cyan]feed[/cyan]          Feed the pet (reduces hunger)\n"
        f"  [cyan]clean[/cyan]         Bathe the pet (restores cleanliness)\n"
        f"  [cyan]play[/cyan]          Mini-game — boosts happiness\n"
        f"  [cyan]sleep[/cyan]         Rest the pet  [dim]--duration HOURS[/dim]\n"
        f"  [cyan]doctor[/cyan]        Heal the pet (restores health)\n"
        f"  [cyan]stats[/cyan]         Detailed system metrics\n"
        f"  [cyan]achievements[/cyan]  Show all achievements\n"
        f"  [cyan]rename NAME[/cyan]   Rename the pet\n"
        f"  [cyan]theme THEME[/cyan]   Change color theme\n"
        f"  [cyan]reset[/cyan]         Delete pet & start fresh\n"
        f"  [cyan]info[/cyan]          Show this help",
        title="ℹ️  About ServerPet", border_style="cyan",
    ))


# ─── Live Watch Dashboard ──────────────────────────────────────────────────────

def cmd_watch(args=None) -> None:
    s  = get_state()
    th = theme(s)
    console.print(f"[{th['primary']}]🔴 Live mode — press Ctrl+C to exit[/{th['primary']}]\n")
    time.sleep(0.5)

    frame = 0

    def build() -> Panel:
        nonlocal frame
        m  = get_metrics()
        st = load_state() or s
        st = update_state(st, m)
        save_state(st)
        th = theme(st)

        display_mood = "playing" if (frame % 20 == 0 and st["mood"] in ("happy","content")) else st["mood"]
        art_lines = pet_art(st, display_mood)
        art_str   = "\n".join(f"    {l}" for l in art_lines)

        mood = st["mood"]
        mc   = mood_color(mood, th)

        def ibar(val, w=14):
            filled = max(0, min(w, int((val/100)*w)))
            b  = "█"*filled + "░"*(w-filled)
            c  = th["secondary"] if val > 65 else th["warning"] if val > 35 else th["danger"]
            return f"[{c}][{b}] {val:5.1f}%[/{c}]"

        def sbar(val, w=14):
            return ibar(100 - val, w)

        # ── Network display ───────────────────────
        lat   = m.get("net_latency")
        ploss = m.get("packet_loss_pct", 0)
        lat_str   = f"{lat}ms" if lat is not None else "??ms"
        lat_color = th["danger"] if lat is None or lat > 200 else th["warning"] if lat > 100 else th["secondary"]
        ploss_color = th["danger"] if ploss > 10 else th["warning"] if ploss > 2 else th["secondary"]

        # ── Alerts ────────────────────────────────
        alerts = []
        if m["cpu"]  > 90: alerts.append(f"[{th['danger']}]⚠  CPU CRITICAL {m['cpu']:.0f}%[/{th['danger']}]")
        if m["ram"]  > 85: alerts.append(f"[{th['danger']}]⚠  RAM HIGH     {m['ram']:.0f}%[/{th['danger']}]")
        if m["disk"] > 90: alerts.append(f"[{th['danger']}]⚠  DISK FULL    {m['disk']:.0f}%[/{th['danger']}]")
        if ploss     > 10: alerts.append(f"[{th['danger']}]😵 PACKET LOSS  {ploss:.1f}%[/{th['danger']}]")
        if lat is not None and lat > 200:
            alerts.append(f"[{th['warning']}]🐌 HIGH LATENCY {lat}ms[/{th['warning']}]")
        if st["hunger"]      > 70: alerts.append(f"[{th['warning']}]🍖  Hungry! → serverpet feed[/{th['warning']}]")
        if st["health"]      < 30: alerts.append(f"[{th['danger']}]💊  Critical! → serverpet doctor[/{th['danger']}]")
        if st["energy"]      < 20: alerts.append(f"[{th['warning']}]💤  Tired!   → serverpet sleep[/{th['warning']}]")
        if st["cleanliness"] < 20: alerts.append(f"[{th['warning']}]🚿  Dirty!   → serverpet clean[/{th['warning']}]")
        alert_block = "\n    ".join(alerts) if alerts else f"[{th['secondary']}]✅  All systems nominal[/{th['secondary']}]"

        temp_row = ""
        if m.get("temp"):
            tc = th["danger"] if m["temp"] > 80 else th["warning"] if m["temp"] > 60 else th["secondary"]
            temp_row = f"\n    [bold]Temp      [/bold][{tc}]{m['temp']}°C[/{tc}]"

        ach_count = len(st.get("achievements", {}))

        body = (
            f"\n"
            f"[{th['pet']}]{art_str}[/{th['pet']}]\n\n"
            f"    [bold]Name      [/bold]{st['name']}  [dim]({st['species'].title()} · {st['personality'].title()})[/dim]\n"
            f"    [bold]Mood      [/bold][{mc}]{mood_icon(mood)} {mood.title()}[/{mc}]\n"
            f"    [bold]Age       [/bold]{st['age_days']:.1f} days  "
            f"[dim]🏆 {ach_count} achievement{'s' if ach_count!=1 else ''}[/dim]\n"
            f"\n"
            f"    [bold]Health    [/bold]{ibar(st['health'])}\n"
            f"    [bold]Hunger    [/bold]{ibar(100-st['hunger'])}\n"
            f"    [bold]Energy    [/bold]{ibar(st['energy'])}\n"
            f"    [bold]Happiness [/bold]{ibar(st['happiness'])}\n"
            f"    [bold]Cleanness [/bold]{ibar(st['cleanliness'])}\n"
            f"\n"
            f"    ── System ──────────────────────────────\n"
            f"    [bold]CPU       [/bold]{sbar(m['cpu'])}\n"
            f"    [bold]RAM       [/bold]{sbar(m['ram'])}\n"
            f"    [bold]Disk      [/bold]{sbar(m['disk'])}\n"
            f"    [bold]Latency   [/bold][{lat_color}]{lat_str}[/{lat_color}]\n"
            f"    [bold]Pkt Loss  [/bold][{ploss_color}]{ploss:.1f}%[/{ploss_color}]\n"
            f"    [bold]Processes [/bold]{m['procs']}\n"
            f"    [bold]Uptime    [/bold][{th['secondary']}]{m['uptime_str']}[/{th['secondary']}]"
            f"{temp_row}\n"
            f"\n"
            f"    ── Alerts ──────────────────────────────\n"
            f"    {alert_block}\n"
            f"\n"
            f"    [dim]Updated {datetime.now().strftime('%H:%M:%S')} · Ctrl+C to exit[/dim]"
        )

        frame += 1
        return Panel(body, title=f"🐾 ServerPet Watch — {st['name']}", border_style=th["primary"], padding=(0,0))

    try:
        with Live(build(), refresh_per_second=0.4, screen=False) as live:
            while True:
                time.sleep(2.5)
                live.update(build())
    except KeyboardInterrupt:
        console.print(f"\n[{th['primary']}]Exiting watch mode. See you later![/{th['primary']}]")


# ─── Argument Parser ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="serverpet",
        description="🐾 ServerPet — Tamagotchi-style virtual pet for your server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run 'serverpet info' for the full command reference.",
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("start", help="Create a new pet")
    p.add_argument("--name",        default="Byte",  help="Pet name (default: Byte)")
    p.add_argument("--species",     default="cat",   choices=SPECIES, help="Pet species")
    p.add_argument("--personality", default=None,    choices=PERSONALITIES)
    p.add_argument("--reset",       action="store_true", help="Delete existing pet first")

    sub.add_parser("status",       help="Pet & system overview")
    sub.add_parser("watch",        help="Live dashboard (auto-refresh)")
    sub.add_parser("feed",         help="Feed the pet")
    sub.add_parser("clean",        help="Clean the pet")
    sub.add_parser("play",         help="Play a mini-game")

    p = sub.add_parser("sleep",    help="Rest the pet")
    p.add_argument("--duration",   type=int, default=8, help="Simulated sleep hours (default: 8)")

    sub.add_parser("doctor",       help="Heal the pet")
    sub.add_parser("stats",        help="Detailed system metrics")
    sub.add_parser("achievements", help="Show achievement board")

    p = sub.add_parser("rename",   help="Give the pet a new name")
    p.add_argument("name",         help="New name")

    p = sub.add_parser("theme",    help="Change color theme")
    p.add_argument("theme",        choices=list(THEMES))

    sub.add_parser("reset",        help="Delete pet & start fresh")
    sub.add_parser("info",         help="Command reference & about")

    args = parser.parse_args()
    cmds = {
        "start": cmd_start, "status": cmd_status, "watch": cmd_watch,
        "feed":  cmd_feed,  "clean":  cmd_clean,  "play":  cmd_play,
        "sleep": cmd_sleep, "doctor": cmd_doctor, "stats": cmd_stats,
        "achievements": cmd_achievements, "rename": cmd_rename,
        "theme": cmd_theme, "reset": cmd_reset,   "info":  cmd_info,
    }

    if args.command is None:
        if STATE_FILE.exists():
            cmd_status()
        else:
            cmd_info()
        return

    fn = cmds.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
