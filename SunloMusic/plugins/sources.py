import asyncio, time, random
from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot, ensure_assistant_in_chat
from SunloMusic.decorators import catch_errors
from SunloMusic.ytdlp import extract_audio
from SunloMusic.calls import play_stream, update_live_timer
from SunloMusic.queues import get_queue, Track
from SunloMusic.config import config
from SunloMusic.formatters import format_duration
from SunloMusic.thumbnails import generate_thumbnail, get_default_thumb
from SunloMusic.keyboards import player_buttons, queue_add_keyboard
from richgram import rich_send, rich_esc
from SunloMusic.database import add_recent
import base64

@bot.on_message(filters.command("splay") & filters.group)
@catch_errors
async def splay_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/splay spotify_link</code>")
    
    query = " ".join(m.command[1:])
    status = await m.reply_text("🔍 <b>Searching Spotify...</b>")
    
    assist_status = await ensure_assistant_in_chat(m.chat.id)
    if assist_status != "ok":
        return await status.edit_text("❌ <b>Assistant could not join the group!</b>")

    info = await extract_audio(query)
    if not info:
        return await status.edit_text("❌ <b>Could not find this song.</b>")
        
    q = get_queue(m.chat.id)
    track = Track(info["title"][:40]+"...", info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, False, video_id=info.get("video_id", ""))
    
    if q.now_playing:
        q.queue.append(track)
        await status.edit_text(f"📥 <b>Added to Queue:</b> {info['title']}")
        return
        
    q.now_playing = track
    q.start_time = time.time()
    q.total_paused = 0
    q.paused = False
    q.votes = set()
    await status.delete()
    
    thumb_url = track.thumbnail or "https://i.ibb.co/68xK6Z4/sunlo-premium.jpg"
    b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
    card_text = f'<img src="{thumb_url}" style="width: 100%; border-radius: 10px; display: block; margin-bottom: 10px;" /><b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href="https://t.me/{config.BOT_USERNAME.strip("@")}?start=dl_{b64_title}">{rich_esc(track.title)}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {format_duration(track.duration)}\n🙋‍♂️ Request: <a href="tg://user?id={track.requester_id}">{rich_esc(track.requester)}</a>'
    
    from SunloMusic.plugins.voice import speak_in_vc
    async def play_with_tts():
        from SunloMusic.database import get_group_setting
        if await get_group_setting(m.chat.id, "tts", False):
            await speak_in_vc(m.chat.id, f"Ab play ho raha hai, {track.title}")
        return await play_stream(m.chat.id, track.url, track.video, duration=track.duration)
        
    sent_msg, _ = await asyncio.gather(rich_send(bot, m.chat.id, card_text + player_buttons(q, 0)), play_with_tts())
    
    q.playing_message_id = sent_msg.id
    try: await sent_msg.pin(disable_notification=True)
    except: pass
    if q.timer_task: q.timer_task.cancel()
    q.timer_task = asyncio.create_task(update_live_timer(m.chat.id, sent_msg.id))

@bot.on_message(filters.command("audiobook") & filters.group)
@catch_errors
async def audiobook_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/audiobook book_name</code>")
    
    query = f"audiobook {' '.join(m.command[1:])}"
    status = await m.reply_text("🔍 <b>Searching Audiobook...</b>")
    
    assist_status = await ensure_assistant_in_chat(m.chat.id)
    if assist_status != "ok":
        return await status.edit_text("❌ <b>Assistant could not join the group!</b>")

    info = await extract_audio(query)
    if not info:
        return await status.edit_text("❌ <b>Could not find this audiobook.</b>")
        
    q = get_queue(m.chat.id)
    track = Track(info["title"][:40]+"...", info["url"], info["duration"], info["thumbnail"], m.from_user.first_name, m.from_user.id, False, video_id=info.get("video_id", ""))
    
    if q.now_playing:
        q.queue.append(track)
        await status.edit_text(f"📥 <b>Added to Queue:</b> {info['title']}")
        return
        
    q.now_playing = track
    q.start_time = time.time()
    q.total_paused = 0
    q.paused = False
    q.votes = set()
    await status.delete()
    
    thumb_url = track.thumbnail or "https://i.ibb.co/68xK6Z4/sunlo-premium.jpg"
    b64_title = base64.urlsafe_b64encode(track.title.encode()).decode().strip("=")
    card_text = f'<img src="{thumb_url}" style="width: 100%; border-radius: 10px; display: block; margin-bottom: 10px;" /><b>🎧🎶 Music Time 🎶🎧</b>\n━━━━━━━━━━━━━\n🎵 <a href="https://t.me/{config.BOT_USERNAME.strip("@")}?start=dl_{b64_title}">{rich_esc(track.title)}</a>\n━━━━━━━━━━━━━\n⏱ Duration: {format_duration(track.duration)}\n🙋‍♂️ Request: <a href="tg://user?id={track.requester_id}">{rich_esc(track.requester)}</a>'
    
    from SunloMusic.plugins.voice import speak_in_vc
    async def play_with_tts():
        from SunloMusic.database import get_group_setting
        if await get_group_setting(m.chat.id, "tts", False):
            await speak_in_vc(m.chat.id, f"Ab play ho raha hai, {track.title}")
        return await play_stream(m.chat.id, track.url, track.video, duration=track.duration)
        
    sent_msg, _ = await asyncio.gather(rich_send(bot, m.chat.id, card_text + player_buttons(q, 0)), play_with_tts())
    
    q.playing_message_id = sent_msg.id
    try: await sent_msg.pin(disable_notification=True)
    except: pass
    if q.timer_task: q.timer_task.cancel()
    q.timer_task = asyncio.create_task(update_live_timer(m.chat.id, sent_msg.id))
