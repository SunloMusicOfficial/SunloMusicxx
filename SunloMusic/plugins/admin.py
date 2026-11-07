import asyncio, time, platform, os, sys, subprocess
from pyrogram import filters
from pyrogram.types import Message, LinkPreviewOptions
from SunloMusic.bot import bot
from SunloMusic.config import config
from SunloMusic.database import set_auth, get_all_chats, get_stats, add_sudo, remove_sudo, sudo_col, is_sudo, set_fsub, set_prefix
from SunloMusic.decorators import sudo_only, admin_only, catch_errors
from SunloMusic.queues import active_chats, get_queue
from SunloMusic.calls import call

START_TIME = time.time()

@bot.on_message(filters.command("auth") & filters.group)
@catch_errors
@admin_only
async def auth_cmd(_, m: Message):
    await set_auth(m.chat.id, True)
    await m.reply_text("✅ <b>Chat Authorized</b>")

@bot.on_message(filters.command("stats"))
@catch_errors
@sudo_only
async def stats_cmd(_, m: Message):
    s = await get_stats()
    uptime_sec = int(time.time() - START_TIME)
    h, rem = divmod(uptime_sec, 3600)
    mins, secs = divmod(rem, 60)
    active_vc = len(active_chats())
    text = (
        f"⚡ <b>『 SYSTEM MONITOR 』</b> ⚡\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"🟢 <b>Status:</b> ONLINE  |  ⏱ <b>Uptime:</b> <code>{h:02d}h {mins:02d}m</code>\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"👥 <b>Users:</b> <code>{s['users']}</code>  |  💬 <b>Chats:</b> <code>{s['chats']}</code>\n"
        f"🎵 <b>Active VCs:</b> <code>{active_vc}</code>\n"
        f"💻 <b>System:</b> <code>Python {platform.python_version()}</code>\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
    )
    await m.reply_text(text)

@bot.on_message(filters.command("broadcast"))
@catch_errors
@sudo_only
async def bc_cmd(_, m: Message):
    if not m.reply_to_message: 
        return await m.reply_text("Reply to a message.")
    chats = await get_all_chats()
    status = await m.reply_text(f"📢 Broadcasting to {len(chats)} chats...")
    success, failed = 0, 0
    for c in chats:
        try: 
            await m.reply_to_message.copy(c)
            success += 1
        except: 
            failed += 1
        await asyncio.sleep(0.1)
    await status.edit_text(f"✅ <b>Broadcast Complete</b>\n\n🟢 Success: {success}\n🔴 Failed: {failed}")

@bot.on_message(filters.command("addsudo"))
@catch_errors
@sudo_only
async def addsudo_cmd(_, m: Message):
    if not m.reply_to_message: 
        return await m.reply_text("Reply to a user.")
    await add_sudo(m.reply_to_message.from_user.id)
    await m.reply_text("✅ <b>Sudo added.</b>")

@bot.on_message(filters.command("delsudo"))
@catch_errors
@sudo_only
async def delsudo_cmd(_, m: Message):
    if len(m.command) < 2: 
        return await m.reply_text("Usage: /delsudo user_id")
    try:
        await remove_sudo(int(m.command[1]))
        await m.reply_text("🗑 <b>Sudo removed.</b>")
    except ValueError:
        await m.reply_text("❌ Invalid ID")

@bot.on_message(filters.command("sudolist"))
@catch_errors
@sudo_only
async def sudolist_cmd(_, m: Message):
    sudos = [u async for u in sudo_col.find({})]
    text = "<b>👑 Sudo Users List</b>\n━━━━━━━━━━━━━\n"
    if not sudos: text += "No sudo users found.\n"
    else:
        for idx, u in enumerate(sudos, 1): text += f"{idx}. <code>{u['user_id']}</code>\n"
    text += "━━━━━━━━━━━━━\n"
    text += f"<b>Owner:</b> <code>{config.OWNER_ID}</code>"
    await m.reply_text(text)

# ✅ FIXED: ACTIVE VC MONITOR
@bot.on_message(filters.command("activevc"))
@catch_errors
@sudo_only
async def activevc_cmd(_, m: Message):
    chats = active_chats()
    if not chats:
        return await m.reply_text("📭 <b>No active Voice Chats right now.</b>")
    
    status = await m.reply_text("📡 <i>Scanning active Voice Chats...</i>")
    text = "⚡ <b>『 ACTIVE VC MONITOR 』</b> ⚡\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
    
    for c in chats:
        q = get_queue(c)
        try:
            chat = await bot.get_chat(c)
            chat_title = chat.title or "Private Group"
            if chat.username:
                link_text = f"<a href='https://t.me/{chat.username}'>🔗 Click Here</a>"
            else:
                try:
                    invite = await bot.export_chat_invite_link(c)
                    link_text = f"<a href='{invite}'>🔗 Join Link</a>"
                except: link_text = "<i>No Public Link</i>"
        except:
            chat_title = "Unknown Group"
            link_text = "<i>No Link Available</i>"

        if q.now_playing:
            song = q.now_playing.title[:25] + ("..." if len(q.now_playing.title) > 25 else "")
            req = q.now_playing.requester
            text += f"🎧 <b>Group:</b> {chat_title}\n{link_text}\n🆔 <b>ID:</b> <code>{c}</code>\n▶️ <b>Playing:</b> <i>{song}</i>\n🙋‍♂️ <b>By:</b> {req}\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        else:
            text += f"🎧 <b>Group:</b> {chat_title}\n{link_text}\n🆔 <b>ID:</b> <code>{c}</code>\n⏳ <b>Status:</b> <i>Connecting...</i>\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            
    text += f"🌐 <b>Total Active VCs:</b> <code>{len(chats)}</code>"
    await status.delete()
    await m.reply_text(text, link_preview_options=LinkPreviewOptions(is_disabled=True))

# ✅ FIXED: RESTART (Render compatible)
@bot.on_message(filters.command("restart"))
@catch_errors
@sudo_only
async def restart_cmd(_, m: Message):
    await m.reply_text("🔄 <b>Restarting SunloMusic...</b>")
    await asyncio.sleep(2)
    # Render automatically restarts the process if it exits with code 1
    os._exit(1)

@bot.on_message(filters.command("fsub") & filters.group)
@catch_errors
@admin_only
async def fsub_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/fsub @YourChannel</code> or <code>/fsub off</code>")
    if m.command[1].lower() == "off":
        await set_fsub(m.chat.id, None)
        return await m.reply_text("✅ <b>Force Subscribe Disabled.</b>")
    channel = m.command[1]
    await set_fsub(m.chat.id, channel)
    await m.reply_text(f"✅ <b>Force Subscribe set to:</b> {channel}")

@bot.on_message(filters.command("setprefix") & filters.group)
@catch_errors
@admin_only
async def setprefix_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/setprefix !</code>")
    prefix = m.command[1]
    if len(prefix) > 1:
        return await m.reply_text("❌ Prefix must be a single character.")
    await set_prefix(m.chat.id, prefix)
    await m.reply_text(f"✅ <b>Prefix changed to:</b> <code>{prefix}</code>")
