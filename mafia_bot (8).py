#!/usr/bin/env python3
"""
🎭 MAFIA TELEGRAM BOT
Exact UI replica from screenshots - MafiaAzBot style
All 21 roles from Russian Mafia rules

SETUP:
1. pip install python-telegram-bot==20.7
2. Get token from @BotFather
3. Set your TOKEN below
4. python mafia_bot.py

COMMANDS:
/start      - Private: Hello + menu buttons
/start@Bot  - Group: Start game recruitment
/rules      - Game rules
"""

import os
import random
import asyncio
from collections import Counter
from enum import Enum

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, filters
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ══════════════════════════════════════════
# ROLES
# ══════════════════════════════════════════

class Team(Enum):
    CITY  = "city"
    MAFIA = "mafia"
    LONER = "loner"

ROLES = {
    # CITY
    "Komissar":      {"team": Team.CITY,  "emoji": "🕵🏼", "short": "Detective",  "desc": "Har raat ek khiladi ko check karo. Agar Mafia mile to vote karo use."},
    "Sergeant":      {"team": Team.CITY,  "emoji": "👮🏼", "short": "Sergeant",   "desc": "Komissar ka sahayak. Komissar mare to uski jagah lo."},
    "Mayor":         {"team": Team.CITY,  "emoji": "🎖️",  "short": "Mayor",      "desc": "Din mein tumhara vote 2 ke barabar hai!"},
    "Doctor":        {"team": Team.CITY,  "emoji": "👨🏼‍⚕️","short": "Doctor",    "desc": "Raat mein kisi ko bachao. Khud ko sirf 1 baar bacha sakte ho."},
    "Lyubovnitsa":   {"team": Team.CITY,  "emoji": "💃",   "short": "Lover",     "desc": "Raat mein kisi ko visit karo - woh koi action nahi kar sakta."},
    "Bomzh":         {"team": Team.CITY,  "emoji": "🧙🏻", "short": "Tramp",     "desc": "Raat mein kisi ke paas jao aur dekho koi aaya kya."},
    "Citizen":       {"team": Team.CITY,  "emoji": "👨🏼",  "short": "Citizen",   "desc": "Aam nagrik. Mafia ko vote karke nikalo."},
    "Schastlivchik": {"team": Team.CITY,  "emoji": "🤞🏼", "short": "Lucky",     "desc": "Tumhare paas 2 zindagiyan hain!"},
    "Samubiyitsa":   {"team": Team.CITY,  "emoji": "🤦🏼", "short": "Suicide",   "desc": "Jeet: Agar din mein vote karke maro. Haaro: Raat mein ya zinda bache."},
    "Kamikaze":      {"team": Team.CITY,  "emoji": "💣",   "short": "Kamikaze",  "desc": "Agar koi tumhe maare, tum bhi use le jaate ho!"},
    # MAFIA
    "Don":           {"team": Team.MAFIA, "emoji": "🤵🏻", "short": "Don",       "desc": "Mafia ka boss. Raat mein target choose karo."},
    "Mafia":         {"team": Team.MAFIA, "emoji": "🤵🏼", "short": "Mafia",     "desc": "Don ke saath milke kisi ko maaro."},
    "Advokat":       {"team": Team.MAFIA, "emoji": "👨🏼‍💼","short": "Lawyer",   "desc": "Mafia member ko protect karo - Komissar unhe Citizen dikhega."},
    "Ubiyitsa":      {"team": Team.MAFIA, "emoji": "🕴️",  "short": "Killer",    "desc": "Kisi ko bhi guaranteed maaro - Doctor bhi nahi bacha sakta!"},
    "Zhurnalist":    {"team": Team.MAFIA, "emoji": "👩🏼‍💻","short": "Journalist","desc": "Raat mein kisi ki role check karo aur Mafia ko bata do."},
    # LONERS
    "Manyak":        {"team": Team.LONER, "emoji": "🔪",   "short": "Maniac",    "desc": "Sabko maaro! Akele jeet lo."},
    "Oboroten":      {"team": Team.LONER, "emoji": "🐺",   "short": "Werewolf",  "desc": "Mafia mare to Mafia bano. Komissar mare to Sergeant bano."},
    "Podzhigatel":   {"team": Team.LONER, "emoji": "🧟",   "short": "Arsonist",  "desc": "Har raat kisi ko mark karo. Khud choose karo to sab maro! 3 maro to jeet."},
    "Mag":           {"team": Team.LONER, "emoji": "🧙",   "short": "Wizard",    "desc": "Don/Maniac/Komissar tumhe nahi maar sakta. Uske baad unhe maaro ya chodo."},
    "Aferist":       {"team": Team.LONER, "emoji": "🤹🏻", "short": "Trickster", "desc": "Kisi ka naam use karo din mein. Zinda raho."},
    "Stukach":       {"team": Team.LONER, "emoji": "🤓",   "short": "Informer",  "desc": "Agar Komissar wali check karo to role public ho jaayegi!"},
}

ROLE_SETS = {
    4:  ["Komissar","Citizen","Don","Mafia"],
    5:  ["Komissar","Doctor","Don","Mafia","Citizen"],
    6:  ["Komissar","Doctor","Don","Mafia","Citizen","Manyak"],
    7:  ["Komissar","Doctor","Don","Mafia","Citizen","Citizen","Manyak"],
    8:  ["Komissar","Doctor","Lyubovnitsa","Don","Mafia","Advokat","Citizen","Manyak"],
    9:  ["Komissar","Sergeant","Doctor","Lyubovnitsa","Don","Mafia","Advokat","Citizen","Manyak"],
    10: ["Komissar","Sergeant","Doctor","Lyubovnitsa","Bomzh","Don","Mafia","Mafia","Advokat","Manyak"],
    11: ["Komissar","Sergeant","Doctor","Lyubovnitsa","Bomzh","Mayor","Don","Mafia","Mafia","Advokat","Manyak"],
    12: ["Komissar","Sergeant","Doctor","Lyubovnitsa","Bomzh","Mayor","Schastlivchik","Don","Mafia","Mafia","Advokat","Ubiyitsa"],
    13: ["Komissar","Sergeant","Doctor","Lyubovnitsa","Bomzh","Mayor","Schastlivchik","Don","Mafia","Mafia","Advokat","Ubiyitsa","Manyak"],
    14: ["Komissar","Sergeant","Doctor","Lyubovnitsa","Bomzh","Mayor","Schastlivchik","Kamikaze","Don","Mafia","Mafia","Advokat","Ubiyitsa","Manyak"],
    15: ["Komissar","Sergeant","Doctor","Lyubovnitsa","Bomzh","Mayor","Schastlivchik","Kamikaze","Don","Mafia","Mafia","Advokat","Ubiyitsa","Zhurnalist","Manyak"],
}

def get_role_set(count):
    if count in ROLE_SETS:
        return list(ROLE_SETS[count])
    best = min(ROLE_SETS.keys(), key=lambda x: abs(x - count))
    base = list(ROLE_SETS[best])
    while len(base) < count:
        base.append("Citizen")
    return base[:count]


# ══════════════════════════════════════════
# GAME STATE
# ══════════════════════════════════════════

class Phase(Enum):
    WAITING  = "waiting"
    NIGHT    = "night"
    DAY      = "day"
    FINISHED = "finished"

class Player:
    def __init__(self, user_id, name, username):
        self.user_id     = user_id
        self.name        = name
        self.username    = username
        self.role        = None
        self.alive       = True
        self.lives       = 1
        self.protected   = False
        self.blocked     = False
        self.vote_weight = 1

    @property
    def display(self):
        return f"@{self.username}" if self.username else self.name

    @property
    def role_data(self):
        return ROLES.get(self.role, {})

    @property
    def team(self):
        return self.role_data.get("team", Team.CITY)

    @property
    def short_role(self):
        return self.role_data.get("short", self.role)


class Game:
    def __init__(self, chat_id):
        self.chat_id       = chat_id
        self.players       = {}
        self.phase         = Phase.WAITING
        self.day           = 0
        self.night_actions = {}
        self.day_votes     = {}
        self.eliminated    = []
        self.join_msg_id   = None
        self.podzhig_marks = []

    @property
    def alive_players(self):
        return [p for p in self.players.values() if p.alive]

    def get_role(self, role):
        return next((p for p in self.alive_players if p.role == role), None)

    def check_winner(self):
        alive   = self.alive_players
        mafia   = [p for p in alive if p.team == Team.MAFIA]
        city    = [p for p in alive if p.team == Team.CITY]
        manyak  = self.get_role("Manyak")
        podzhig = self.get_role("Podzhigatel")

        if manyak and len(alive) <= 2:
            return ("Maniac", manyak)
        if podzhig and len(alive) <= 1:
            return ("Arsonist", podzhig)
        if not mafia:
            return ("City", None)
        if len(mafia) >= len(city):
            return ("Mafia", None)
        return None


GAMES = {}

def get_game(cid):
    return GAMES.get(cid)

# ══════════════════════════════════════════
# /start PRIVATE — like screenshot 1
# ══════════════════════════════════════════

async def cmd_start_private(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("➕ Add game to your chat",
            url=f"https://t.me/{(await ctx.bot.get_me()).username}?startgroup=go")],
        [InlineKeyboardButton("🎲 Premium groups", callback_data="premium")],
        [InlineKeyboardButton("📰 News", callback_data="news")],
        [InlineKeyboardButton("🌍 Language", callback_data="language"),
         InlineKeyboardButton("📋 Game rules", callback_data="rules_btn")],
    ]
    await update.message.reply_text(
        "Hello!\nI'm a bot presenter for playing the **Mafia**.",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )

# ══════════════════════════════════════════
# GROUP GAME
# ══════════════════════════════════════════

async def cmd_newgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_chat.type == "private":
        await update.message.reply_text("Group mein use karo!")
        return
    if chat_id in GAMES and GAMES[chat_id].phase not in [Phase.WAITING, Phase.FINISHED]:
        await update.message.reply_text("⚠️ Game pehle se chal raha hai!")
        return

    game = Game(chat_id)
    GAMES[chat_id] = game

    kb = [[InlineKeyboardButton("✅  Join to the game", callback_data=f"join_{chat_id}")]]
    msg = await update.message.reply_text(
        "🎭 **The game is being recruited**\n\n"
        "👥 Players: 0  _(min 4 needed)_\n\n"
        "Press button below to join!",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    game.join_msg_id = msg.message_id


async def cmd_join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Backup /join command — same as clicking the Join button"""
    chat_id = update.effective_chat.id
    game    = get_game(chat_id)
    user    = update.effective_user

    if not game or game.phase != Phase.WAITING:
        await update.message.reply_text("⚠️ Koi active game nahi! Pehle /newgame karo."); return
    if user.id in game.players:
        await update.message.reply_text(f"✅ {user.first_name}, tum pehle se join ho!"); return
    if len(game.players) >= 15:
        await update.message.reply_text("⚠️ Game full hai! Max 15 players."); return

    p = Player(user.id, user.first_name, user.username)
    game.players[user.id] = p
    count = len(game.players)
    plines = "\n".join(f"  {i+1}. {pl.display}" for i, pl in enumerate(game.players.values()))

    kb = [[InlineKeyboardButton("✅  Join to the game", callback_data=f"join_{chat_id}")]]
    if count >= 4:
        kb.append([InlineKeyboardButton("🚀  Start the game!", callback_data=f"sg_{chat_id}")])

    try:
        await ctx.bot.edit_message_text(
            chat_id=chat_id, message_id=game.join_msg_id,
            text=(
                f"🎭 **The game is being recruited**\n\n"
                f"👥 Players: {count}  {'✅ Ready!' if count >= 4 else f'({4-count} more needed)'}\n\n"
                f"{plines}"
            ),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown"
        )
    except Exception:
        pass

    m = await update.message.reply_text(f"✅ **{user.first_name}** has joined the game!", parse_mode="Markdown")
    await asyncio.sleep(5)
    try: await ctx.bot.delete_message(chat_id, m.message_id)
    except Exception: pass


async def cb_join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q       = update.callback_query
    await q.answer()
    chat_id = int(q.data.split("_")[1])
    game    = get_game(chat_id)
    user    = q.from_user

    if not game or game.phase != Phase.WAITING:
        await q.answer("Game available nahi!", show_alert=True); return
    if user.id in game.players:
        await q.answer("Pehle se join ho! ✅", show_alert=True); return
    if len(game.players) >= 15:
        await q.answer("Game full hai!", show_alert=True); return

    p = Player(user.id, user.first_name, user.username)
    game.players[user.id] = p
    count = len(game.players)

    plines = "\n".join(f"  {i+1}. {pl.display}" for i, pl in enumerate(game.players.values()))
    kb = [[InlineKeyboardButton("✅  Join to the game", callback_data=f"join_{chat_id}")]]
    if count >= 4:
        kb.append([InlineKeyboardButton("🚀  Start the game!", callback_data=f"sg_{chat_id}")])

    try:
        await ctx.bot.edit_message_text(
            chat_id=chat_id, message_id=game.join_msg_id,
            text=(
                f"🎭 **The game is being recruited**\n\n"
                f"👥 Players: {count}  {'✅ Ready!' if count >= 4 else f'({4-count} more needed)'}\n\n"
                f"{plines}"
            ),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # Notify joined
    m = await ctx.bot.send_message(chat_id, f"✅ **{user.first_name}** has joined the game!", parse_mode="Markdown")
    await asyncio.sleep(5)
    try: await ctx.bot.delete_message(chat_id, m.message_id)
    except Exception: pass


async def cb_startgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("Starting...")
    chat_id = int(q.data.split("_")[1])
    game    = get_game(chat_id)
    if not game or game.phase != Phase.WAITING: return
    if len(game.players) < 4:
        await q.answer("Min 4 players!", show_alert=True); return
    await begin_game(chat_id, ctx)


async def cmd_force_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game    = get_game(chat_id)
    if not game or game.phase != Phase.WAITING:
        await update.message.reply_text("⚠️ Waiting game nahi hai."); return
    if len(game.players) < 4:
        await update.message.reply_text(f"⚠️ Min 4 chahiye. Abhi: {len(game.players)}"); return
    await begin_game(chat_id, ctx)


async def begin_game(chat_id, ctx):
    game  = get_game(chat_id)
    count = len(game.players)
    roles = get_role_set(count)
    random.shuffle(roles)
    plist = list(game.players.values())
    random.shuffle(plist)

    for i, player in enumerate(plist):
        player.role = roles[i]
        if player.role == "Schastlivchik": player.lives = 2
        if player.role == "Mayor":         player.vote_weight = 2

    game.phase = Phase.NIGHT
    game.day   = 1

    # Role summary like screenshot: "Citizen - 2, Detective, Don"
    tc = {}
    for p in game.players.values():
        tc[p.short_role] = tc.get(p.short_role, 0) + 1
    role_summary = ", ".join(f"{r} - {c}" if c > 1 else r for r, c in tc.items())

    # Send private roles
    failed = []
    for player in game.players.values():
        rd = ROLES[player.role]
        try:
            await ctx.bot.send_message(
                player.user_id,
                f"🎭 **Your role: {rd['emoji']} {player.role}**\n\n"
                f"_{rd['desc']}_\n\n"
                f"Team: **{'City 🏙️' if rd['team']==Team.CITY else 'Mafia 🤵' if rd['team']==Team.MAFIA else 'Loner 🎭'}**",
                parse_mode="Markdown"
            )
        except Exception:
            failed.append(player.display)

    # Mafia team info
    for mp in [p for p in game.players.values() if p.team == Team.MAFIA]:
        ti = "\n".join(
            f"  {ROLES[p.role]['emoji']} {p.display} — {p.role}"
            for p in game.players.values() if p.team == Team.MAFIA
        )
        try:
            await ctx.bot.send_message(mp.user_id, f"🤫 **Your Mafia team:**\n{ti}", parse_mode="Markdown")
        except Exception: pass

    alive_list = "\n".join(f"  {i+1}. {p.display}" for i, p in enumerate(game.alive_players))
    warn = ("\n\n⚠️ These players must /start bot in private:\n" + "\n".join(failed)) if failed else ""

    await ctx.bot.send_message(
        chat_id,
        f"🎭 **Game started!**\n\n"
        f"**Alive players:**\n{alive_list}\n\n"
        f"Of them: {role_summary}\nTotal: {count}" + warn,
        parse_mode="Markdown"
    )
    await asyncio.sleep(2)
    await start_night(chat_id, ctx)


# ══════════════════════════════════════════
# NIGHT
# ══════════════════════════════════════════

async def start_night(chat_id, ctx):
    game = get_game(chat_id)
    game.phase = Phase.NIGHT
    game.night_actions = {}
    for p in game.alive_players:
        p.protected = False
        p.blocked   = False

    await ctx.bot.send_message(
        chat_id,
        f"🌙 **Night {game.day}**\n\nThe city fell asleep... 😴\nRoles are making their moves in private chat.",
        parse_mode="Markdown"
    )
    await send_night_buttons(chat_id, ctx)
    asyncio.create_task(auto_night_end(chat_id, ctx, game.day))


async def send_night_buttons(chat_id, ctx):
    game = get_game(chat_id)
    PROMPTS = {
        "Komissar":    "🔍 **Detective** — Kise check karna hai?",
        "Sergeant":    "🔍 **Sergeant** — Kise check karo?",
        "Doctor":      "💊 **Doctor** — Kise bachana hai?",
        "Lyubovnitsa": "💃 **Lover** — Kise visit karo? (woh action nahi kar sakta)",
        "Bomzh":       "🍶 **Tramp** — Kiske ghar jao?",
        "Don":         "🔫 **Don** — Aaj raat kise maara jaye?",
        "Mafia":       "🔫 **Mafia** — Target choose karo:",
        "Advokat":     "⚖️ **Lawyer** — Kise protect karo?",
        "Ubiyitsa":    "🗡️ **Killer** — Kise guaranteed maaro?",
        "Zhurnalist":  "📰 **Journalist** — Kise check karo?",
        "Manyak":      "🔪 **Maniac** — Aaj raat ka shikaar?",
        "Podzhigatel": "🔥 **Arsonist** — Kise mark karo?",
        "Stukach":     "🤓 **Informer** — Kise check karo?",
        "Aferist":     "🃏 **Trickster** — Kiska naam kal use karo?",
    }

    for player in game.alive_players:
        if player.role not in PROMPTS:
            continue

        targets = [p for p in game.alive_players if p.user_id != player.user_id]
        keyboard = [
            [InlineKeyboardButton(f"👤 {t.display}", callback_data=f"na_{player.user_id}_{t.user_id}_{chat_id}")]
            for t in targets
        ]

        if player.role == "Doctor":
            keyboard.append([InlineKeyboardButton("💊 Khud ko bachao", callback_data=f"na_{player.user_id}_{player.user_id}_{chat_id}")])
        if player.role == "Podzhigatel":
            keyboard.append([InlineKeyboardButton("🔥 IGNITE — Sab jalaao!", callback_data=f"na_{player.user_id}_{player.user_id}_{chat_id}")])

        try:
            await ctx.bot.send_message(
                player.user_id,
                f"🌙 **Night {game.day}**\n\n{PROMPTS[player.role]}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        except Exception:
            game.night_actions[player.user_id] = None


async def auto_night_end(chat_id, ctx, day_num):
    await asyncio.sleep(90)
    game = get_game(chat_id)
    if game and game.phase == Phase.NIGHT and game.day == day_num:
        await resolve_night(chat_id, ctx)


async def cb_night_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q     = update.callback_query
    await q.answer()
    parts = q.data.split("_")
    if len(parts) != 4: return

    _, actor_id, target_id, chat_id = parts
    actor_id  = int(actor_id)
    target_id = int(target_id)
    chat_id   = int(chat_id)
    game      = get_game(chat_id)

    if not game or game.phase != Phase.NIGHT:
        await q.edit_message_text("⚠️ Raat ka time nahi hai!"); return

    actor = game.players.get(actor_id)
    if not actor: return

    if actor_id in game.night_actions and game.night_actions[actor_id] is not None:
        await q.edit_message_text("✅ Action pehle se register hai!"); return

    game.night_actions[actor_id] = target_id
    target = game.players.get(target_id)
    t_name = "Khud ko" if actor_id == target_id else (target.display if target else "?")
    await q.edit_message_text(f"✅ Done! Tumne choose kiya: **{t_name}**", parse_mode="Markdown")

    # Check if all done
    active = {"Komissar","Sergeant","Doctor","Lyubovnitsa","Bomzh",
              "Don","Mafia","Advokat","Ubiyitsa","Zhurnalist",
              "Manyak","Podzhigatel","Stukach","Aferist"}
    need  = [p for p in game.alive_players if p.role in active]
    acted = [p for p in need if p.user_id in game.night_actions]
    if len(acted) >= len(need):
        await resolve_night(chat_id, ctx)


# ══════════════════════════════════════════
# NIGHT RESOLUTION
# ══════════════════════════════════════════

async def resolve_night(chat_id, ctx):
    game = get_game(chat_id)
    if not game or game.phase != Phase.NIGHT: return

    actions = game.night_actions
    killed  = set()
    msgs    = []

    # Lyubovnitsa block
    lyub = game.get_role("Lyubovnitsa")
    if lyub and actions.get(lyub.user_id):
        bt = game.players.get(actions[lyub.user_id])
        if bt: bt.blocked = True

    # Doctor protect
    doc = game.get_role("Doctor")
    if doc and actions.get(doc.user_id) and not doc.blocked:
        pt = game.players.get(actions[doc.user_id])
        if pt: pt.protected = True

    # Advokat
    adv = game.get_role("Advokat")
    adv_target = actions.get(adv.user_id) if adv else None

    # Mafia kills
    mafia_all = [p for p in game.alive_players if p.team == Team.MAFIA
                 and p.role not in ["Advokat","Zhurnalist"]]
    mafia_votes = [actions[p.user_id] for p in mafia_all
                   if p.user_id in actions and actions[p.user_id] and not p.blocked]

    mafia_target_id = None
    if mafia_votes:
        mafia_target_id = Counter(mafia_votes).most_common(1)[0][0]
        mt = game.players.get(mafia_target_id)
        if mt and mt.alive and not mt.protected:
            killed.add(mafia_target_id)
            if mt.role == "Kamikaze":
                for mp in mafia_all: killed.add(mp.user_id)
                msgs.append(f"💥 **{mt.display}** (Kamikaze) dhamake ke saath gaya — Mafia bhi saath!!")

    # Ubiyitsa
    ub = game.get_role("Ubiyitsa")
    if ub and actions.get(ub.user_id) and not ub.blocked:
        ubt = game.players.get(actions[ub.user_id])
        if ubt and ubt.alive:
            killed.add(ubt.user_id)
            if ubt.role == "Kamikaze": killed.add(ub.user_id)

    # Manyak
    mn = game.get_role("Manyak")
    if mn and actions.get(mn.user_id) and not mn.blocked:
        mnt = game.players.get(actions[mn.user_id])
        if mnt and not mnt.protected:
            killed.add(mnt.user_id)

    # Podzhigatel
    pj = game.get_role("Podzhigatel")
    if pj and actions.get(pj.user_id):
        if actions[pj.user_id] == pj.user_id:
            for uid in game.podzhig_marks: killed.add(uid)
            killed.add(pj.user_id)
            msgs.append(f"🔥 **{pj.display}** (Arsonist) ne sab ko jala diya!!")
        else:
            game.podzhig_marks.append(actions[pj.user_id])

    # Komissar check
    kom = game.get_role("Komissar")
    if kom and actions.get(kom.user_id) and not kom.blocked:
        kt = game.players.get(actions[kom.user_id])
        if kt:
            adv_prot = (adv_target == kt.user_id)
            result = "Citizen 👤" if adv_prot else ("MAFIA! 🚨" if kt.team == Team.MAFIA else "Citizen ✅")
            try:
                await ctx.bot.send_message(kom.user_id, f"🔍 **Check result:** {kt.display} → **{result}**", parse_mode="Markdown")
            except Exception: pass

    # Zhurnalist check
    zhur = game.get_role("Zhurnalist")
    if zhur and actions.get(zhur.user_id) and not zhur.blocked:
        zjt = game.players.get(actions[zhur.user_id])
        if zjt:
            try:
                await ctx.bot.send_message(zhur.user_id, f"📰 **Intel:** {zjt.display} → **{zjt.role}** {ROLES[zjt.role]['emoji']}", parse_mode="Markdown")
            except Exception: pass

    # Bomzh
    bomzh = game.get_role("Bomzh")
    if bomzh and actions.get(bomzh.user_id) and not bomzh.blocked:
        bzt = actions[bomzh.user_id]
        if bzt in killed:
            visitor = "Don" if mafia_all else "Unknown"
            try:
                await ctx.bot.send_message(bomzh.user_id, f"🧙🏻 **Dekha!** {game.players[bzt].display} ke ghar **{visitor}** aaya tha!", parse_mode="Markdown")
            except Exception: pass

    # Stukach
    st = game.get_role("Stukach")
    if st and actions.get(st.user_id):
        if actions[st.user_id] == actions.get(kom.user_id if kom else None):
            rp = game.players.get(actions[st.user_id])
            if rp:
                msgs.append(f"🤓 **Informer Reveal:** {rp.display} ki role hai **{rp.role}** {ROLES[rp.role]['emoji']}")

    # Process deaths - like screenshot style
    death_msgs = []
    for uid in killed:
        p = game.players.get(uid)
        if not p or not p.alive: continue

        if p.lives > 1:
            p.lives -= 1
            death_msgs.append(f"🤞🏼 **{p.display}** (Lucky) bachh gaya! {p.lives} life bachi.")
        else:
            p.alive = False
            game.eliminated.append(p)

            # Find who visited (like screenshot: "They say that his guest was Don")
            visitor_role = None
            for uid2, tid2 in actions.items():
                if tid2 == uid and uid2 != uid:
                    vp = game.players.get(uid2)
                    if vp: visitor_role = vp.short_role; break

            line = f"Today **{p.short_role}** {p.display} was brutally murdered..."
            if visitor_role:
                line += f"\nThey say that his guest was **{visitor_role}**"
            death_msgs.append(line)

    # ── Morning announcement ──
    morning = "🌅 **Morning has come!**\n\n"
    if not death_msgs and not msgs:
        morning += "😴 The night passed peacefully... No one was killed!\n"
    else:
        morning += "\n\n".join(death_msgs + msgs)

    # Alive list like screenshot
    alive_list = "\n".join(f"  {i+1}. {p.display}" for i, p in enumerate(game.alive_players))
    tc = {}
    for p in game.alive_players: tc[p.short_role] = tc.get(p.short_role, 0) + 1
    role_sum = ", ".join(f"{r} - {c}" if c > 1 else r for r, c in tc.items())

    morning += (
        f"\n\n**Alive players:**\n{alive_list}\n\n"
        f"Of them: {role_sum}\nTotal: {len(game.alive_players)}"
    )

    game.phase = Phase.DAY
    await ctx.bot.send_message(chat_id, morning, parse_mode="Markdown")

    winner = game.check_winner()
    if winner:
        await announce_winner(chat_id, ctx, winner); return

    await asyncio.sleep(3)
    await start_day_vote(chat_id, ctx)


# ══════════════════════════════════════════
# DAY VOTING
# ══════════════════════════════════════════

async def start_day_vote(chat_id, ctx):
    game = get_game(chat_id)
    game.phase     = Phase.DAY
    game.day_votes = {}

    kb = [
        [InlineKeyboardButton(f"🗳 {p.display}", callback_data=f"vote_{p.user_id}_{chat_id}")]
        for p in game.alive_players
    ]
    kb.append([InlineKeyboardButton("⏩ Nobody (skip)", callback_data=f"vote_skip_{chat_id}")])

    await ctx.bot.send_message(
        chat_id,
        f"☀️ **Day {game.day} — City Meeting**\n\nWho should be eliminated? Vote now!\n_(60 seconds)_",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    asyncio.create_task(auto_day_end(chat_id, ctx, game.day))


async def cb_day_vote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q     = update.callback_query
    await q.answer()
    parts = q.data.split("_")
    voter = q.from_user

    if len(parts) == 3:
        _, target_str, chat_id_str = parts
    else: return

    chat_id = int(chat_id_str)
    game    = get_game(chat_id)
    if not game or game.phase != Phase.DAY:
        await q.answer("Voting time nahi!", show_alert=True); return

    vp = game.players.get(voter.id)
    if not vp or not vp.alive:
        await q.answer("Tum game mein nahi ho!", show_alert=True); return
    if voter.id in game.day_votes:
        await q.answer("Pehle se vote kar chuke ho!", show_alert=True); return

    game.day_votes[voter.id] = target_str
    await q.answer("✅ Vote registered!")

    if len(game.day_votes) >= len(game.alive_players):
        await resolve_day(chat_id, ctx)


async def auto_day_end(chat_id, ctx, day_num):
    await asyncio.sleep(60)
    game = get_game(chat_id)
    if game and game.phase == Phase.DAY and game.day == day_num:
        await resolve_day(chat_id, ctx)


async def resolve_day(chat_id, ctx):
    game = get_game(chat_id)
    if not game or game.phase != Phase.DAY: return

    vc = Counter()
    for vid, t in game.day_votes.items():
        if t == "skip": continue
        vp = game.players.get(vid)
        w  = vp.vote_weight if vp else 1
        try: vc[int(t)] += w
        except ValueError: pass

    res = "🗳 **Voting results:**\n"
    for uid, votes in vc.most_common():
        p = game.players.get(uid)
        if p: res += f"  {p.display}: **{votes}** votes\n"
    skip = sum(1 for t in game.day_votes.values() if t == "skip")
    if skip: res += f"  ⏩ Skip: {skip} votes\n"

    await ctx.bot.send_message(chat_id, res, parse_mode="Markdown")

    ep = None
    if vc:
        top_uid = vc.most_common(1)[0][0]
        ep      = game.players.get(top_uid)

    if ep:
        if ep.role == "Samubiyitsa":
            ep.alive = False
            await ctx.bot.send_message(chat_id,
                f"🤦🏼 **{ep.display}** (Suicide) has won! This is exactly what they wanted!", parse_mode="Markdown")
        elif ep.role == "Kamikaze":
            ep.alive = False
            await ctx.bot.send_message(chat_id,
                f"💣 **{ep.display}** (Kamikaze) is leaving... and taking someone along!", parse_mode="Markdown")
            top_voter = max(
                (uid for uid, t in game.day_votes.items() if t == str(top_uid)),
                key=lambda uid: game.players[uid].vote_weight if game.players.get(uid) else 0,
                default=None
            )
            if top_voter and game.players.get(top_voter):
                tv = game.players[top_voter]; tv.alive = False
                await ctx.bot.send_message(chat_id,
                    f"💥 **{tv.display}** ({tv.short_role}) was taken by Kamikaze!", parse_mode="Markdown")
        else:
            ep.alive = False
            await ctx.bot.send_message(chat_id,
                f"👋 **{ep.display}** ({ROLES[ep.role]['emoji']} **{ep.role}**) has been eliminated!",
                parse_mode="Markdown")
    else:
        await ctx.bot.send_message(chat_id, "😤 No one was eliminated today.", parse_mode="Markdown")

    winner = game.check_winner()
    if winner:
        await announce_winner(chat_id, ctx, winner); return

    game.day += 1
    await asyncio.sleep(3)
    await start_night(chat_id, ctx)


# ══════════════════════════════════════════
# GAME OVER — like screenshot 5
# ══════════════════════════════════════════

async def announce_winner(chat_id, ctx, winner_tuple):
    game = get_game(chat_id)
    team, winner_player = winner_tuple

    if team == "City":
        winners = [p for p in game.players.values() if p.team == Team.CITY]
        others  = [p for p in game.players.values() if p.team != Team.CITY]
    elif team == "Mafia":
        winners = [p for p in game.players.values() if p.team == Team.MAFIA]
        others  = [p for p in game.players.values() if p.team != Team.MAFIA]
    else:
        winners = [winner_player] if winner_player else []
        others  = [p for p in game.players.values() if p.user_id != (winner_player.user_id if winner_player else 0)]

    win_text = "\n".join(
        f"  {i+1}. {p.display} - {p.short_role}" for i, p in enumerate(winners)
    )
    other_text = "\n".join(
        f"  {i+len(winners)+1}. {p.display} - {p.short_role}" for i, p in enumerate(others)
    )
    emoji = {"City":"🏙️","Mafia":"🤵","Maniac":"🔪","Arsonist":"🔥"}.get(team,"🏆")

    kb = [[InlineKeyboardButton("🔄 Play again!", callback_data=f"again_{chat_id}")]]

    await ctx.bot.send_message(
        chat_id,
        f"🏆 **Game Over**\n\n"
        f"**Winners: {emoji} {team}**\n{win_text or '  —'}\n\n"
        f"**Other users:**\n{other_text or '  —'}\n\n"
        f"The game lasted: {game.day} minutes",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    game.phase = Phase.FINISHED


async def cb_play_again(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    chat_id = int(q.data.split("_")[1])
    game    = Game(chat_id)
    GAMES[chat_id] = game
    kb = [[InlineKeyboardButton("✅  Join to the game", callback_data=f"join_{chat_id}")]]
    msg = await ctx.bot.send_message(
        chat_id,
        "🎭 **The game is being recruited**\n\n👥 Players: 0  _(min 4 needed)_\n\nPress button below to join!",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )
    game.join_msg_id = msg.message_id


# ══════════════════════════════════════════
# MISC CALLBACKS & COMMANDS
# ══════════════════════════════════════════

async def cb_misc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.data == "premium":
        await q.answer("Premium coming soon! 🎲", show_alert=True)
    elif q.data == "language":
        await q.answer("Language: English 🇬🇧 / Hindi 🇮🇳", show_alert=True)
    elif q.data == "news":
        await q.answer("No news yet!", show_alert=True)
    elif q.data == "rules_btn":
        await q.answer()
        await send_rules(q.message.chat_id, ctx)


async def send_rules(chat_id, ctx):
    text = "📋 **MAFIA — ALL ROLES**\n\n🏙️ **CITY:**\n"
    for role, info in ROLES.items():
        if info["team"] == Team.CITY:
            text += f"{info['emoji']} **{role}:** {info['desc']}\n\n"
    text += "🤵 **MAFIA:**\n"
    for role, info in ROLES.items():
        if info["team"] == Team.MAFIA:
            text += f"{info['emoji']} **{role}:** {info['desc']}\n\n"
    text += "🎭 **LONERS:**\n"
    for role, info in ROLES.items():
        if info["team"] == Team.LONER:
            text += f"{info['emoji']} **{role}:** {info['desc']}\n\n"

    for part in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        await ctx.bot.send_message(chat_id, part, parse_mode="Markdown")


async def cmd_rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await send_rules(update.effective_chat.id, ctx)


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game    = get_game(chat_id)
    if not game:
        await update.message.reply_text("Koi game nahi. /newgame se shuru karo!"); return

    if game.phase == Phase.WAITING:
        plist = "\n".join(f"  {i+1}. {p.display}" for i, p in enumerate(game.players.values()))
        await update.message.reply_text(
            f"⏳ **Recruitment — {len(game.players)}/4 min**\n\n{plist or '  (koi nahi)'}",
            parse_mode="Markdown"); return

    alive_str = "\n".join(f"  {p.display}" for p in game.alive_players)
    dead_str  = "\n".join(f"  💀 {p.display} ({p.short_role})" for p in game.eliminated) or "  —"
    await update.message.reply_text(
        f"🎮 **Day {game.day} — {game.phase.value.upper()}**\n\n"
        f"**Alive ({len(game.alive_players)}):**\n{alive_str}\n\n"
        f"**Eliminated:**\n{dead_str}",
        parse_mode="Markdown")


async def cmd_skip_night(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    game = get_game(update.effective_chat.id)
    if game and game.phase == Phase.NIGHT:
        await resolve_night(update.effective_chat.id, ctx)


async def cmd_skip_day(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    game = get_game(update.effective_chat.id)
    if game and game.phase == Phase.DAY:
        await resolve_day(update.effective_chat.id, ctx)


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start",      cmd_start_private, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("start",      cmd_newgame,       filters=filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("newgame",    cmd_newgame))
    app.add_handler(CommandHandler("join",       cmd_join))
    app.add_handler(CommandHandler("start_game", cmd_force_start))
    app.add_handler(CommandHandler("status",     cmd_status))
    app.add_handler(CommandHandler("rules",      cmd_rules))
    app.add_handler(CommandHandler("skip_night", cmd_skip_night))
    app.add_handler(CommandHandler("skip_day",   cmd_skip_day))

    # Callbacks
    app.add_handler(CallbackQueryHandler(cb_join,         pattern=r"^join_"))
    app.add_handler(CallbackQueryHandler(cb_startgame,    pattern=r"^sg_"))
    app.add_handler(CallbackQueryHandler(cb_night_action, pattern=r"^na_"))
    app.add_handler(CallbackQueryHandler(cb_day_vote,     pattern=r"^vote_"))
    app.add_handler(CallbackQueryHandler(cb_play_again,   pattern=r"^again_"))
    app.add_handler(CallbackQueryHandler(cb_misc,         pattern=r"^(premium|language|news|rules_btn)"))

    print("🎭 Mafia Bot running! Token:", TOKEN[:10] + "...")
    app.run_polling()

if __name__ == "__main__":
    main()
