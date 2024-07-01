# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import random
lock = asyncio.Lock()
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, LANGUAGES, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, FILE_REQ_CHANNEL, HOW_TO_DOWNLOAD, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, LOG_CHANNEL, PICS, HS_PICS, MESSAGE_LOG_CHANNEL, SELF_DELETE_SECONDS, SELF_DELETE, LOGIN_CHANNEL, JOIN_PICS, YT_PICS
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_shortlink, get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, mute_login
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
file_req_channel = FILE_REQ_CHANNEL

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
FILTER_MODE = {}

@Client.on_message(filters.command('autofilter'))
async def fil_mod(client, message): 
      mode_on = ["yes", "on", "true"]
      mode_of = ["no", "off", "false"]

      try: 
         args = message.text.split(None, 1)[1].lower() 
      except: 
         return await message.reply("**ɪɴᴄᴏᴍᴩʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ...**")
      
      m = await message.reply("**sᴇᴛᴛɪɴɢs.../**")

      if args in mode_on:
          FILTER_MODE[str(message.chat.id)] = "True" 
          await m.edit("**ᴀᴜᴛᴏ-ғɪʟᴛᴇʀ ᴇɴᴀʙʟᴇᴅ**")
      
      elif args in mode_of:
          FILTER_MODE[str(message.chat.id)] = "False"
          await m.edit("**ᴀᴜᴛᴏ-ғɪʟᴛᴇʀ ᴅɪsᴀʙʟᴇᴅ**")
      else:
          await m.edit("Usᴇ :- /autofilter on Oʀ /autofilter off")

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        content = message.text
        if LOGIN_CHANNEL and not await mute_login(client, message):
            try:
                invite_link = await client.create_chat_invite_link(int(LOGIN_CHANNEL))
            except ChatAdminRequired:
                logger.error("Make sure Bot is admin in Forcesub channel")
                return
            buttons = [[
                InlineKeyboardButton("» ᴊᴏɪɴ ᴛʜᴇ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ «", url=invite_link.invite_link)
            ],[
                InlineKeyboardButton("⟲ ᴛʀʏ ᴀɢᴀɪɴ ⟳", callback_data="grp_checksub")
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            try:
                await client.restrict_chat_member(message.chat.id, message.from_user.id, ChatPermissions(), datetime.datetime.now() + datetime.timedelta(minutes=5))
            except:
                pass
            k = await message.reply_photo(
                photo=random.choice(JOIN_PICS),
                caption=f"<b>ʜᴇʟʟᴏ {message.from_user.mention}\n\n⚠️ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⚠️\n\n{content} ᴀᴠᴀɪʟᴀʙʟᴇ...!\n\n✘ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴏᴜʀ ʙᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ sᴏ ʏᴏᴜ ᴅᴏɴ'ᴛ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ.\n\n✘ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ᴊᴏɪɴ ʙᴜᴜᴛᴏɴ ᴀɴᴅ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ,ᴛʜᴇɴ ᴄʟɪᴄᴋ 🔄 ᴛʀʏ ᴀɢᴀɪɴ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ</b>",
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(200)
            await k.delete()
            try:
                await message.delete()
            except:
                pass
        else:
            await auto_filter(client, message)

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    await message.reply_text("<b>ʜᴇʏ ᴅᴜᴅᴇ🥰,\n\nʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ᴍᴏᴠɪᴇ ʜᴇʀᴇ........\nAꜱᴋ ᴍᴏᴠɪᴇ ᴏɴ ᴏᴜʀ ɢʀᴏᴜᴘ\nᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴊᴏɪɴ👇</b>",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ ", url=f"https://t.me/sillunu_oru_movies/5")]]))
    await bot.send_message(
        chat_id=MESSAGE_LOG_CHANNEL,
        text=f"<b>#ᴩᴍ_ᴍꜱɢ💌\n\nName : {user}\n\nID : {user_id}\n\nMessage : {content}</b>"
    )

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("oKda", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    btn.insert(0, 
        [
            InlineKeyboardButton("🔊 sᴇʟᴇᴄᴛ ʏᴏᴜʀ ʟᴀɴɢᴜᴀɢᴇs 🔊", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
        ]
    )
    btn.insert(1, 
         [
             InlineKeyboardButton(f'🔖 ɪɴꜰᴏ', 'reqinfo'),
             InlineKeyboardButton(f'♻️ ᴍᴏᴠɪᴇ', 'minfo')
         ]
    )
    btn.append(
         [
             InlineKeyboardButton("🤔𝗛𝗼𝘄 𝗧𝗼 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱🤔", url=f"{HOW_TO_DOWNLOAD}")
         ]
    )
    if 0 < offset <= 6:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 6
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⇇ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 ᴩᴀɢᴇs {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ⇉", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⇇ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ ⇉", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("okDa", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Iᴀᴍ Cʜᴇᴄᴋɪɴɢ U Asᴋᴇᴅ Fɪʟᴇ Iɴ Mʏ Dʙ...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
             k = await query.message.edit('Sᴏʀʀʏ Pʟᴇᴀsᴇ Cʜᴇᴄᴋ Yᴏᴜʀ Sᴩᴇʟʟɪɴɢ Iɴ Gᴏᴏɢʟᴇ Fɪʀsᴛ ﹦ Iғ Yᴏᴜʀ Sᴩᴇʟʟɪɴɢ Cᴏʀʀᴇᴄᴛ Mᴇᴀɴs Tʜᴀᴛ Fɪʟᴇ Nᴏᴛ Fᴏᴜʙᴅ Iɴ Mʏ Dᴀᴛᴀʙᴀsᴇ 💌')
             await asyncio.sleep(30)
             await k.delete()

#languages

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):

    if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
        return await query.answer(
            f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
            show_alert=True,
        )
    
    _, search, key = query.data.split("#")

    btn = [
        [
            InlineKeyboardButton(
                text=lang.title(),
                callback_data=f"fl#{lang.lower()}#{search}#{key}"
                ),
        ]
        for lang in LANGUAGES
    ]

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="☟ ʟᴀɴɢᴜᴀɢᴇs ☟", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="⇇ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ⇉", callback_data=f"next_{req}_{key}_{offset}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, search, key = query.data.split("#")

    search = search.replace("_", " ")
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    if int(req) not in [query.message.reply_to_message.from_user.id, 0]:
        return await query.answer(
            f"⚠️ ʜᴇʟʟᴏ{query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇQᴜᴇꜱᴛ,\nʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
            show_alert=True,
        )

    search = f"{search} {lang}" 

    files, _, _ = await get_search_results(chat_id, search, max_results=10)
    files = [file for file in files if re.search(lang, file.file_name, re.IGNORECASE)]
    if not files:
        await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    btn.insert(0, 
        [
            InlineKeyboardButton("🤔 𝗛𝗼𝘄 𝗧𝗼 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 🤔", url=f"{HOW_TO_DOWNLOAD}")
        ]
    )
    btn.insert(1, 
         [
             InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
             InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo')
         ]
    )
    offset = 0
    btn.append(
         [
            InlineKeyboardButton(text="⇇ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ⇉",callback_data=f"next_{req}_{key}_{offset}")
         ]
    )
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))

#languages


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Tʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ!! Cᴏɴɴᴇᴄᴛ ᴛᴏ ꜱᴏᴍᴇ ɢʀᴏᴜᴘꜱ ғɪʀꜱᴛ.", quote=True)
                    return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')
            else:
                await query.message.edit_text(
                    "Iᴀᴍ Nᴏᴛ Cᴏɴɴᴇᴄᴛᴇᴅ Tᴏ Aɴʏ Gʀᴏᴜᴩ \nCʜᴇᴄᴋ /connections Oʀ Cᴏɴɴᴇᴄᴛ Tᴏ Aɴʏ Gʀᴏᴜᴩ",
                    quote=True
                )
                return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Tʜᴀᴛ´s Nᴏᴛ Fᴏʀ Yᴏᴜ !!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("🚫 Dᴇʟᴇᴛᴇ 🚫", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Dɪsᴄᴏɴɴᴇᴄᴛᴇᴅ Fʀᴏᴍ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Sᴜᴄᴄᴇssғᴜʟʟʏ Cᴏɴɴᴇᴄᴛɪᴏɴ Dᴇʟᴇᴛᴇᴅ"
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('Cʟɪᴄᴋ Bᴀᴄᴋ Bᴜᴛᴛᴏɴ ➥ Yᴏᴜ Sᴇᴇ Mʏ Nᴀᴍᴇ Aɴᴅ Pʀᴏғɪʟᴇ ➥ Tᴏᴜᴄʜ Mʏ Nᴀᴍᴇ', show_alert=True)
        except UserIsBlocked:
            await query.answer('Fɪʀsᴛ Sᴛᴀʀᴛ Tʜᴇ Bᴏᴛ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("Yᴏ Yᴏ Fɪʀsᴛ Jᴏɪɴ Tʜᴇ Cʜᴀɴɴᴇʟ ᴀɴᴅ Cʟɪᴄᴋ Rᴇғʀᴇsʜ 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ Sᴜᴄʜ Fɪʟᴇ Exɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    
    elif query.data == "grp_checksub":
        user = query.message.reply_to_message.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ʀᴇǫᴜᴇsᴛ ᴀɢᴀɪɴ.", show_alert=True)
            return
        await query.answer(f"ʜᴇʟʟᴏ {query.from_user.first_name},\nɢᴏᴏᴅ, ᴄᴀɴ ʏᴏᴜ ʀᴇǫᴜᴇsᴛ ɴᴏᴡ !", show_alert=True)
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"<b>ғᴇᴛᴄʜɪɴɢ ғɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} ᴏɴ ᴅᴀᴛᴀʙᴀsᴇ...ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text(f"<b>ғᴏᴜɴᴅ {total} ғɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇss ᴡɪʟʟ sᴛᴀʀᴛ ɪɴ 5 sᴇᴄᴏɴᴅs!</b>")
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'ғɪʟᴇ ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<b>ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ. sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
            except Exception as e:
                logger.exception(e)
                await query.message.edit_text(f'ᴇʀʀᴏʀ: {e}')
            else:
                await query.message.edit_text(f"<b>ᴘʀᴏᴄᴇss ᴄᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ !\n\nsᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}.</b>")

    elif query.data == "reqinfo":
        await query.answer("⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nᴀꜰᴛᴇʀ 10 ᴍɪɴᴜᴛᴇꜱ ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇᴅ\n\nɪꜰ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ꜱᴇᴇ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴍᴏᴠɪᴇ / sᴇʀɪᴇs ꜰɪʟᴇ, ʟᴏᴏᴋ ᴀᴛ ᴛʜᴇ ɴᴇxᴛ ᴘᴀɢᴇ", show_alert=True)

    elif query.data == "minfo":
        await query.answer("⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\nᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ\n⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\n\nɢᴏ ᴛᴏ ɢᴏᴏɢʟᴇ ➠ ᴛʏᴘᴇ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ ➠ ᴄᴏᴘʏ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ ➠ ᴘᴀꜱᴛᴇ ᴛʜɪꜱ ɢʀᴏᴜᴘ\n\nᴇxᴀᴍᴘʟᴇ : ᴀᴠᴀᴛᴀʀ: ᴛʜᴇ ᴡᴀʏ ᴏғ ᴡᴀᴛᴇʀ\n\n🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)", show_alert=True)

    elif query.data == "sinfo":
        await query.answer("⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\nꜱᴇʀɪᴇꜱ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ\n⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\n\nɢᴏ ᴛᴏ ɢᴏᴏɢʟᴇ ➠ ᴛʏᴘᴇ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ ➠ ᴄᴏᴘʏ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ ➠ ᴘᴀꜱᴛᴇ ᴛʜɪꜱ ɢʀᴏᴜᴘ\n\nᴇxᴀᴍᴘʟᴇ : ᴍᴏɴᴇʏ ʜᴇɪsᴛ S01E01\n\n🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)", show_alert=True)      

    elif query.data == "rendering_info":
        await query.answer(text=script.RENDERING_TXT, show_alert=True)

    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('⇌ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ⇌', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('🧑‍💻 ᴏᴡɴᴇʀ', callback_data="owner_info"),
            InlineKeyboardButton('💥 sᴜᴘᴘᴏʀᴛ', callback_data="yt_channel")
        ], [
            InlineKeyboardButton('💠 ʜᴇʟᴘ 💠', callback_data='help'),
            InlineKeyboardButton('♻️ ᴀʙᴏᴜᴛ ♻️', callback_data='about')
         ],[
            InlineKeyboardButton('🔥𝙎ɪʟʟᴜɴᴜ 𝙊ʀᴜ 𝙈ᴏᴠɪᴇꜱ🔥', callback_data='supportchannel')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="◉ ○ ○"
        )
        await query.message.edit_text(
            text="◉ ◉ ○"
        )
        await query.message.edit_text(
            text="◉ ◉ ◉"
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
       )
    elif query.data == "help":
        buttons = [[
        ], [
            InlineKeyboardButton('🍷 ᴍᴏʀᴇ ғᴇᴀᴛᴜʀᴇs 🍷', callback_data='help1')
        ], [
            InlineKeyboardButton('ᴍᴀɴᴜᴀʟ ғɪʟᴛᴇʀ', callback_data='manuelfilter'),
            InlineKeyboardButton('ᴀᴜᴛᴏ ғɪʟᴛᴇʀ', callback_data='autofilter')
        ], [
            InlineKeyboardButton('ᴄᴏɴɴᴇᴄᴛɪᴏɴ', callback_data='coct'),
            InlineKeyboardButton('ᴇxᴛʀᴀ ᴍᴏᴅs', callback_data='extra')
        ], [
            InlineKeyboardButton('ғɪʟᴇ sᴛᴏʀᴇ', callback_data='store_file'),
            InlineKeyboardButton('ʀᴏᴜʟs', callback_data='rule_btn')
        ], [
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇉', callback_data='start'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(                     
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "yt_channel":
        buttons = [[
            #InlineKeyboardButton('ʏᴏᴜᴛᴜʙᴇ-ᴄʜᴀɴɴᴇʟ', url="https://www.youtube.com/@hs_bots")
        #],[
            InlineKeyboardButton('ʀǫ-ɢʀᴏᴜᴘ', url="https://t.me/sillunu_oru_movies/5"),
            InlineKeyboardButton('ᴄʜᴀɴɴᴇʟ', url="https://t.me/+rQzZkhBRfDMzMGY1")
        ],[
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇs', url="https://t.me/sillunu_oru_movies"),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url="https://t.me/sillunu_oru_movies")
        ],[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇉', callback_data='start'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(YT_PICS))
        )
        await query.message.edit_text(
            text=script.YT_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "help1":
        buttons = [[
            InlineKeyboardButton('ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ', callback_data='tele')
        ],[
            InlineKeyboardButton('sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ', callback_data='song')
        ],[
            InlineKeyboardButton('ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ', callback_data='video')
        ],[
            InlineKeyboardButton('sᴛɪᴄᴋᴇʀ ɪᴅ', callback_data='sticker')
        ],[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ ⇉', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.FEATURES_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('🍂 sᴛᴀᴛᴜs', callback_data='stats'),
            InlineKeyboardButton('🍒 sᴏᴜʀᴄᴇ', callback_data='source')
        ],[
            InlineKeyboardButton('🛰 ʀᴇɴᴅᴇʀɪɴɢ ɪɴꜰᴏ ☁️', callback_data='rendering_info')
        ],[
            InlineKeyboardButton('♙ ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('ᴄʟᴏsᴇ ↻', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "owner_info":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.OWNER_INFO,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "supportchannel":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(HS_PICS))
        )
        await query.message.edit_text(
            text=script.SUPPORTCHANNEL_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help'),
            InlineKeyboardButton('ʙᴜᴛᴛᴏɴs', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help'),
            InlineKeyboardButton('♙ ᴀᴅᴍɪɴ ♙', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
         )
    elif query.data == "rule_btn":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.RULE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "store_file":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.FILE_STORE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "song":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help1')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SONG_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "video":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help1')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.VIDEO_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tele":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help1')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TELE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "sticker":
        buttons = [[
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='help1')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.STICKER_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        ) 
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('↺ ʀᴇғʀᴇsʜ ↻', callback_data='rfrsh'),
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('↻ ʀᴇғʀᴇsʜ ↺', callback_data='rfrsh'),
            InlineKeyboardButton('⇇ ʙᴀᴄᴋ ⇉', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('ꜰɪʟᴛᴇʀ ʙᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ꜱɪɴɢʟᴇ' if settings["button"] else 'ᴅᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ʙᴏᴛ ᴩᴍ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ ᴏɴ' if settings["botpm"] else '✘ ᴏғғ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴩʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ ᴏɴ' if settings["file_secure"] else '✘ ᴏғғ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ɪᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ ᴏɴ' if settings["imdb"] else '✘ ᴏғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜱᴩᴇʟʟ ᴄʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ ᴏɴ' if settings["spell_check"] else '✘ ᴏғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴡᴇʟᴄᴏᴍᴇ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ ᴏɴ' if settings["welcome"] else '✘ ᴏғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('❣️ᴩʟᴇᴀꜱᴇ ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴩᴩᴏʀᴛ❣️')


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(message.chat.id ,search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    key = f"{message.chat.id}-{message.id}"
    BUTTONS[key] = search
    btn.insert(0, 
        [
            InlineKeyboardButton("🔊 sᴇʟᴇᴄᴛ ʏᴏᴜʀ ʟᴀɴɢᴜᴀɢᴇs 🔊", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
        ]
    )
    btn.insert(1, 
         [
             InlineKeyboardButton(f'🔖 ɪɴꜰᴏ', 'reqinfo'),
             InlineKeyboardButton(f'♻️ ᴍᴏᴠɪᴇ', 'minfo')
         ]
    )
    btn.append(
         [
             InlineKeyboardButton("🤔 𝗛𝗼𝘄 𝗧𝗼 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 🤔", url=f"{HOW_TO_DOWNLOAD}")
         ]
    )
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="ɴᴇxᴛ ⇉", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>📟 ᴛɪᴛʟᴇ : {search} \n📂ᴛᴏᴛᴀʟ ꜰɪʟᴇs ꜰᴏᴜɴᴅᴇᴅ : {str(total_results)}\n👩🏻‍💻 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ : {message.from_user.mention} \n\n⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 𝟷𝟶 ᴍɪɴᴜᴛᴇs.\n\n\n🔊 ☟ ꜱᴇʟᴇᴄᴛ ʏᴏᴜʀ ʟᴀɴɢᴜᴀɢᴇꜱ ☟ 🔊</b>"
    if imdb and imdb.get('poster'):
        try:
            hehe =  await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                      reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(SELF_DELETE_SECONDS)
                await hehe.delete()

        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(SELF_DELETE_SECONDS)
                await hmm.delete()
        except Exception as e:
            logger.exception(e)
            fek = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(SELF_DELETE_SECONDS)
                await fek.delete()
    else:
        fuk = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
        if SELF_DELETE:
            await asyncio.sleep(SELF_DELETE_SECONDS)
            await fuk.delete()


async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("I couldn't find any movie in that name.")
        await asyncio.sleep(8)
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply("I couldn't find anything related to that. Check your spelling")
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    await msg.reply("I couldn't find anything related to that\nDid you mean any one of these?",
                    reply_markup=InlineKeyboardMarkup(btn))


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
