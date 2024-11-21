
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from database.database import db
from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3
from helper_func import encode
from lazydeveloperr.lazy_forcesub import lazy_force_sub, is_subscribed
from config import *
from motor.motor_asyncio import AsyncIOMotorClient  
Dbclient = AsyncIOMotorClient(DB_URI)
Cluster = Dbclient['Cluster0']
Data = Cluster['users']


@Bot.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.command(['start','users','broadcast','batch','genlink','stats']))
async def channel_post(client: Client, message: Message):
    # user = message.from_user
    # if not await db.is_user_exist(user.id):
    #     await db.add_user(user.id) 
    id = message.from_user.id
    if not await db.present_user(id):
        try:
            await db.add_user(id)
            print('user added to db')
        except Exception as e:
            print(f"Error adding user: {e}")
            pass

    if (FORCE_SUB_CHANNEL or FORCE_SUB_CHANNEL2 or FORCE_SUB_CHANNEL3) and not await is_subscribed(client, message):
        # User is not subscribed to any of the required channels, trigger force_sub logic
        return await lazy_force_sub(client, message)

    reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')],
        [InlineKeyboardButton("🚀 Rename", callback_data='rename')]
        ])

    await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)

@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):

    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')],
        [InlineKeyboardButton("🚀 Rename", callback_data="rename")]
        ])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
