import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from telegraph import upload_file
from utils import get_file_id


@Client.on_message(filters.command("telegraph") & filters.private)
async def telegraph_upload(bot, update):
    replied = update.reply_to_message
    if not replied:
        await update.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ / ᴠɪᴅᴇᴏ ᴜɴᴅᴇʀ 5ᴍʙ")
        return
    file_info = get_file_id(replied)
    if not file_info:
        await update.reply_text(" ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ !")
        return
    text = await update.reply_text(text="<code>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪɴ ᴍʏ sᴇʀᴠᴇʀ...</code>", disable_web_page_preview=True)   
    media = await update.reply_to_message.download()   
    await text.edit_text(text="<code>ᴅᴏᴡɴʟᴏᴀᴅ ᴛᴏ ᴍʏ sᴇʀᴠᴇʀ ɪs ᴄᴏᴍᴩʟᴇᴛᴇ. ɴᴏᴡ ɪ ᴀᴍ ᴜᴩʟᴏᴀᴅɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴩʜ...</code>", disable_web_page_preview=True)                                            
    try:
        response = upload_file(media)
    except Exception as error:
        print(error)
        await text.edit_text(text=f"ᴇʀʀᴏʀ :- {error}", disable_web_page_preview=True)       
        return    
    try:
        os.remove(media)
    except Exception as error:
        print(error)
        return    
    await text.edit_text(
        text=f"<b>ʟɪɴᴋ :-</b>\n\n<code>https://graph.org{response[0]}</code>",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup( [[
            InlineKeyboardButton(text="ᴏᴩᴇɴ ʟɪɴᴋ", url=f"https://graph.org{response[0]}"),
            InlineKeyboardButton(text="ꜱʜᴀʀᴇ ʟɪɴᴋ", url=f"https://telegram.me/share/url?url=https://graph.org{response[0]}")
            ],[
            InlineKeyboardButton(text="✗ ᴄʟᴏsᴇ ✗", callback_data="close")
            ]])
        )
    
