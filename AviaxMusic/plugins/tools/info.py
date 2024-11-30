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
    caption = section("<u><b>ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b></u>", body)
    return [caption, None]


async def get_chat_info(chat, already=False):
    if not already:
        chat = await app.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type_ = str(chat.type).split(".")[1]
    is_scam = chat.is_scam
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    link = f"<a href='t.me/username'>link</a>" if username else "Null"
    dc_id = chat.dc_id
    body = {
        "● ᴄʜᴀᴛ ɪᴅ": chat_id,
        "● ᴄʜᴀᴛ ᴅᴄ ɪᴅ": dc_id,
        "● ᴛʏᴘᴇ": type_,
        "● ɴᴀᴍᴇ": [title],
        "● ᴜsᴇʀɴᴀᴍᴇ": [("@" + username) if username else "Null"],
        "● ᴍᴇɴᴛɪᴏɴ": [link],
        "● ᴍᴇᴍʙᴇʀs": members,
        "● sᴄᴀᴍ": is_scam,
        "● ʀᴇsᴛʀɪᴄᴛᴇᴅ": is_restricted,
        "● ᴅᴇsᴄʀɪᴘᴛɪᴏɴ": [description],
    }
    caption = section("<u><b>ᴄʜᴀᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b></u>", body)
    return [caption, None]


@app.on_message(filters.command("info"))
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user = message.text.split(None, 1)[1]

    m = await message.reply_text("<b>ᴘʀᴏᴄᴇssɪɴɢ . . .</b>")

    try:
        info_caption, _ = await get_user_info(user)  # Ignore photo_id
    except Exception as e:
        return await m.edit(f"{str(e)}, Perhaps you meant to use /groupinfo?")

    await m.edit(info_caption, disable_web_page_preview=True)  # Directly send the caption


@app.on_message(filters.command("groupinfo"))
async def chat_info_func(_, message: Message):
    splited = message.text.split()
    if len(splited) == 1:
        chat = message.chat.id
        if chat == message.from_user.id:
            return await message.reply_text(
                "<b>ᴜsᴀɢᴇ:</b> /groupinfo [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ]"
            )
    else:
        chat = splited[1]
    try:
        m = await message.reply_text("<b>ᴘʀᴏᴄᴇssɪɴɢ . . .</b>")

        info_caption, _ = await get_chat_info(chat)  # Ignore photo_id
        await m.edit(info_caption, disable_web_page_preview=True)  # Directly send the caption
    except Exception as e:
        await m.edit(str(e))