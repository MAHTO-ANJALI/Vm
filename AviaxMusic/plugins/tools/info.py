import os

from pyrogram import filters
from pyrogram.types import Message

from AviaxMusic.misc import SUDOERS
from AviaxMusic import app
from AviaxMusic.core.sections import section
from AviaxMusic.utils.database import is_gbanned_user, user_global_karma

__MODULE__ = "Info"
__HELP__ = """
/info [USERNAME|ID] - Get info about a user.
/chat_info [USERNAME|ID] - Get info about a chat.
"""


async def get_user_info(user, already=False):
    if not already:
        user = await app.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    mention = user.mention("Link")
    dc_id = user.dc_id
    is_gbanned = await is_gbanned_user(user_id)
    is_sudo = user_id in SUDOERS
    is_premium = user.is_premium
    karma = await user_global_karma(user_id)
    body = {
        "● ᴜsᴇʀ ɪᴅ": user_id,
        "● ɴᴀᴍᴇ": [first_name],
        "● ᴜsᴇʀɴᴀᴍᴇ": [("@" + username) if username else "Null"],
        "● ᴍᴇɴᴛɪᴏɴ": [mention],
        "● ᴜsᴇʀ ᴅᴄ ɪᴅ": dc_id,
        "● ᴜsᴇʀ sᴜᴅᴏ": is_sudo,
        "● ᴘʀᴇᴍɪᴜᴍ": is_premium,
        "● ᴋᴀʀᴍᴀ": karma,
        "● ɢʟᴏʙᴀʟ-ʙᴀɴ": is_gbanned,
    }
    caption = section("User info", body)
    return [caption, None]


@app.on_message(filters.command("info"))
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user = message.text.split(None, 1)[1]

    m = await message.reply_text("Processing")

    try:
        info_caption, _ = await get_user_info(user)  # Ignore photo_id
    except Exception as e:
        return await m.edit(f"{str(e)}, Perhaps you meant to use /chat_info?")

    await m.edit(info_caption, disable_web_page_preview=True)  # Directly send the caption


@app.on_message(filters.command("chat_info"))
async def chat_info_func(_, message: Message):
    splited = message.text.split()
    if len(splited) == 1:
        chat = message.chat.id
        if chat == message.from_user.id:
            return await message.reply_text(
                "**Usage:**/chat_info [USERNAME|ID]"
            )
    else:
        chat = splited[1]
    try:
        m = await message.reply_text("Processing")

        info_caption, photo_id = await get_chat_info(chat)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)

        photo = await app.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)

        await m.delete()
        os.remove(photo)
    except Exception as e:
        await m.edit(e)