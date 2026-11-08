from pyrogram import filters
from SunloMusic.bot import bot


def cmd_filter(*commands):
    """
    Matches both:
      /command
      /command@BotUsername
    Bot username is read at message-time, so no hardcoding.
    """
    async def func(_, __, message):
        if not message.text:
            return False
        text = message.text.strip()
        if not text.startswith("/"):
            return False

        parts = text.split()
        if not parts:
            return False

        cmd_part = parts[0][1:]  # strip leading "/"

        if "@" in cmd_part:
            cmd, username = cmd_part.split("@", 1)
            if username.lower() != bot.me.username.lower():
                return False
        else:
            cmd = cmd_part

        return cmd.lower() in [c.lower() for c in commands]

    return filters.create(func)
