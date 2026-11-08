from pyrogram import filters
from pyrogram.types import Message
from SunloMusic.bot import bot
from SunloMusic.decorators import catch_errors
from SunloMusic.plugins.play import start_play

@bot.on_message(filters.command("splay") & filters.group)
@catch_errors
async def splay_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/splay spotify_link</code>")
    query = " ".join(m.command[1:])
    await start_play(bot, m, query, video=False)

@bot.on_message(filters.command("audiobook") & filters.group)
@catch_errors
async def audiobook_cmd(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ <b>Usage:</b> <code>/audiobook book_name</code>")
    query = f"audiobook {' '.join(m.command[1:])}"
    await start_play(bot, m, query, video=False)
